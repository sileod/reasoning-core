#!/usr/bin/env python3
"""Deprecated in-memory rebuild for reasoning-core/procedural-pile.

Smoke-test mode (fast, no upload):
  python scripts/rc_preprocess_upload_deprecated.py --smoke_test 50000
Full run:
  python scripts/rc_preprocess_upload_deprecated.py
"""

import os, json, random, argparse, signal, time, html, sys, traceback, shutil, multiprocessing as mp, threading, contextlib, glob, re, gc, heapq
from array import array

base = os.environ["HOME"]
tmp_root = os.environ.get("TMPDIR", f"{base}/tmp")
for name in ("TMPDIR", "TEMP", "TMP"):
    os.environ.setdefault(name, tmp_root)
os.makedirs(tmp_root, exist_ok=True)
import tempfile; tempfile.tempdir = tmp_root

import numpy as np, polars as pl, pyarrow as pa
import pyarrow.compute as pc
import datasets
from datasets import load_dataset, Dataset, DatasetDict, concatenate_datasets, disable_caching, Features, Value
from tqdm import tqdm
from reasoning_core import list_tasks, score_answer
from easydict import EasyDict as edict
from distractor_retrieval import VerificationDistractorRetriever
disable_caching()

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GENERATED_DATA_DIR = os.path.join(REPO_ROOT, "reasoning_core", "generated_data")


class RegexDict(dict):
    def get(self, key, default=None):
        for pattern, value in self.items():
            if re.fullmatch(pattern, key):
                return value
        return default


SOURCE_DATASET_NAMES = RegexDict({
    r"rg.*": "reasoning-gym",
    r"rc.*high": "formal-reasoning-env",
})


TARGET_FEATURES = {
    "procedural-pile": Features({
        "task": Value("large_string"),
        "prompt": Value("large_string"),
        "answer": Value("large_string"),
        "metadata": Value("large_string"),
        "cot": Value("large_string"),
        "level": Value("int64"),
        "mode": Value("large_string"),
    }),
    "reasoning-gym": Features({
        "prompt": Value("large_string"),
        "answer": Value("large_string"),
        "metadata": Value("large_string"),
        "task": Value("large_string"),
        "level": Value("int64"),
        "mode": Value("large_string"),
    }),
}


# ── timing ───────────────────────────────────────────────────────────────────

_timings = {}
_RUN_DIR = None
_KEEP_WORK_DIR = False
_SCORE_DEVNULL = None


def _cleanup_work_dir():
    global _RUN_DIR, _SCORE_DEVNULL
    if _SCORE_DEVNULL is not None:
        try:
            _SCORE_DEVNULL.close()
        except Exception:
            pass
        _SCORE_DEVNULL = None
    if _RUN_DIR and _KEEP_WORK_DIR:
        print(f"kept work dir: {_RUN_DIR}", flush=True)
    elif _RUN_DIR:
        path = _RUN_DIR
        gc.collect()
        try:
            shutil.rmtree(path)
        except OSError as exc:
            print(f"WARN failed to clean work dir {path}: {exc}", flush=True)
        else:
            print(f"cleaned work dir: {path}", flush=True)
        _RUN_DIR = None

class _step:
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        print(f"{self.name}…", flush=True)
        self._t = time.time()
        return self
    def __exit__(self, *_):
        dt = time.time() - self._t
        _timings[self.name] = dt
        print(f"  ↳ {dt:.1f}s", flush=True)


@contextlib.contextmanager
def _heartbeat(label, every=30):
    stop = threading.Event()

    def beat():
        t0 = time.time()
        while not stop.wait(every):
            print(f"  {label}: {time.time() - t0:.0f}s elapsed", flush=True)

    thread = threading.Thread(target=beat, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=0.1)


# ── helpers ───────────────────────────────────────────────────────────────────

def _logical_batches(ds, cols, batch_size=100_000):
    cols = [cols] if isinstance(cols, str) else list(cols)
    table = ds.data.table.select(cols)
    idx = getattr(ds, "_indices", None)
    if idx is None:
        yield from table.to_batches(max_chunksize=batch_size)
        return

    idx_col = idx.column(0)
    for start in range(0, len(ds), batch_size):
        n = min(batch_size, len(ds) - start)
        physical = pa.array(idx_col.slice(start, n).to_numpy(zero_copy_only=False))
        yield from table.take(physical).to_batches(max_chunksize=batch_size)


def deduplicate_by_column(ds, column="prompt", batch_size=100_000):
    """Deduplicate without Hugging Face Dataset.filter's per-row Python overhead."""
    import xxhash

    seen = set()
    keep = array("Q")
    n0 = ds.num_rows
    row_i = 0

    for rb in tqdm(_logical_batches(ds, column, batch_size), desc="deduplicating"):
        for value in rb.column(column).to_pylist():
            h = xxhash.xxh64_intdigest(str(value).encode())
            if h not in seen:
                seen.add(h)
                keep.append(row_i)
            row_i += 1

    removed = n0 - len(keep)
    report = {
        "before": n0,
        "after": len(keep),
        "removed": removed,
        "removed_pct": round(100 * removed / max(n0, 1), 2),
    }
    if removed:
        indices = np.frombuffer(keep, dtype=np.uint64).astype(np.int64, copy=False)
        ds = ds.select(indices)
    del keep, seen
    gc.collect()
    return ds, report


def filter_by_string_length(ds, column="prompt", max_chars=50_000, batch_size=100_000):
    keep = array("Q")
    row_i = 0
    for rb in tqdm(_logical_batches(ds, column, batch_size), desc=f"filter {column} length"):
        lengths = pc.fill_null(pc.utf8_length(rb.column(column)), max_chars)
        valid = np.asarray(pc.less(lengths, max_chars).to_numpy(zero_copy_only=False), dtype=bool)
        keep.extend((row_i + np.flatnonzero(valid)).tolist())
        row_i += len(valid)

    if len(keep) == len(ds):
        return ds
    indices = np.frombuffer(keep, dtype=np.uint64).astype(np.int64, copy=False)
    out = ds.select(indices)
    del keep, indices
    gc.collect()
    return out


def prettyorder_low_memory(ds, cols="task", n_pretty=3, seed=42, batch_size=100_000):
    cols = [cols] if isinstance(cols, str) else list(cols)
    print("building groups...", flush=True)
    groups = {}
    row_i = 0
    for rb in tqdm(_logical_batches(ds, cols, batch_size), desc="grouping"):
        columns = [rb.column(col).to_pylist() for col in cols]
        for values in zip(*columns):
            key = values[0] if len(values) == 1 else tuple(values)
            groups.setdefault(key, array("Q")).append(row_i)
            row_i += 1

    sorted_keys = sorted(groups)
    prefix_n = sum(min(n_pretty, len(groups[key])) for key in sorted_keys)
    indices = np.empty(row_i, dtype=np.int64)
    pos = 0
    for cycle in range(n_pretty):
        for key in sorted_keys:
            rows = groups[key]
            if cycle < len(rows):
                indices[pos] = rows[cycle]
                pos += 1
    for key in sorted_keys:
        tail = np.frombuffer(groups[key], dtype=np.uint64)[n_pretty:]
        indices[pos:pos + len(tail)] = tail
        pos += len(tail)

    np.random.default_rng(seed).shuffle(indices[prefix_n:])
    print(f"prettyorder: {prefix_n:,} interleaved rows "
          f"({n_pretty}x{len(sorted_keys):,} groups) + "
          f"{len(indices) - prefix_n:,} shuffled")
    out = ds.select(indices)
    del groups, indices
    gc.collect()
    return out


def count_by_column(ds, key="task", batch_size=100_000):
    counts = {}
    for rb in _logical_batches(ds, key, batch_size):
        for value in rb.column(key).to_pylist():
            counts[value] = counts.get(value, 0) + 1
    return counts


def subsample(ds, top_k, key="task", seed=42):
    if len(ds) == 0 or top_k <= 0:
        return ds
    counts = count_by_column(ds, key=key)
    sorted_counts = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    if len(sorted_counts) <= top_k:
        return ds
    limit = int(sorted_counts[top_k][1])
    rng = random.Random(seed)
    seen = {task: 0 for task in counts}
    reservoirs = {task: array("Q") for task in counts}

    row_i = 0
    for rb in _logical_batches(ds, key, 100_000):
        for task in rb.column(key).to_pylist():
            seen[task] += 1
            reservoir = reservoirs[task]
            if len(reservoir) < limit:
                reservoir.append(row_i)
            else:
                j = rng.randrange(seen[task])
                if j < limit:
                    reservoir[j] = row_i
            row_i += 1

    n_indices = sum(map(len, reservoirs.values()))
    indices = np.fromiter(
        (i for reservoir in reservoirs.values() for i in reservoir),
        dtype=np.int64,
        count=n_indices,
    )
    indices.sort()
    return ds.select(indices)


class _Timeout(Exception): pass


_WORKER_POOLS = None
_WORKER_MAX_TRIES = 2
_WORKER_SCORE_TIMEOUT = 1.0
_WORKER_NEGATIVE_STRATEGY = "scored_same_task"


def _metadata_obj(metadata):
    if isinstance(metadata, dict):
        return metadata
    try:
        return json.loads(metadata or "{}")
    except Exception:
        return {}


def _token_count(metadata, default=0):
    obj = _metadata_obj(metadata)
    try:
        return int(obj.get("_prompt_tokens", 0)) + int(obj.get("_answer_tokens", 0))
    except Exception:
        return default


def _metadata_level(metadata):
    obj = _metadata_obj(metadata)
    try:
        return int(obj.get("_level", obj.get("level", 0)) or 0)
    except Exception:
        return 0


def _metadata_task(row, meta):
    task = str(row.get("task") or meta.get("_task") or meta.get("task") or "")
    if task == "reasoning_gym" and meta.get("source_dataset"):
        return str(meta["source_dataset"])
    return task


def infer_dataset_name(source):
    if source == "staging":
        return "procedural-pile"
    return SOURCE_DATASET_NAMES.get(os.path.basename(source.rstrip("/")), os.path.basename(source.rstrip("/")))


def resolve_local_source(source):
    if os.path.exists(source):
        return os.path.abspath(source)
    generated_path = os.path.join(GENERATED_DATA_DIR, source)
    if os.path.exists(generated_path):
        return generated_path
    raise FileNotFoundError(
        f"source '{source}' is neither 'staging', an existing path, nor a generated_data key under {GENERATED_DATA_DIR}"
    )


def local_jsonl_files(path):
    if os.path.isfile(path):
        files = [path]
    else:
        files = sorted(glob.glob(os.path.join(path, "*.jsonl")))
    if not files:
        raise FileNotFoundError(f"no .jsonl files found in {path}")
    return files


def normalize_columns(ds):
    missing = {"mode", "cot", "level"} - set(ds.column_names)
    if not missing:
        return ds

    def add_missing(batch):
        n = len(next(iter(batch.values())))
        out = {}
        if "mode" in missing:
            out["mode"] = ["instruct"] * n
        if "cot" in missing:
            out["cot"] = [""] * n
        if "level" in missing:
            out["level"] = [_metadata_level(m) for m in batch.get("metadata", ["{}"] * n)]
        return out

    return ds.map(add_missing, batched=True, desc="normalize schema")


LOCAL_COLUMNS = ["prompt", "answer", "metadata", "task", "cot", "level", "mode"]


def normalize_local_row(row):
    metadata = row.get("metadata", "{}")
    if isinstance(metadata, dict):
        metadata = json.dumps(metadata, ensure_ascii=False)
    elif metadata is None:
        metadata = "{}"
    else:
        metadata = str(metadata)
    meta = _metadata_obj(metadata)
    return {
        "prompt": str(row.get("prompt", "")),
        "answer": str(row.get("answer", "")),
        "metadata": metadata,
        "task": _metadata_task(row, meta),
        "cot": str(row.get("cot") or meta.get("cot") or ""),
        "level": int(row.get("level", _metadata_level(metadata)) or 0),
        "mode": str(row.get("mode") or "instruct"),
    }


def load_local_jsonl_sharded(files, out_dir, shard_rows=100_000):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    shard_paths, pending = [], {col: [] for col in LOCAL_COLUMNS}

    def flush():
        if not pending["prompt"]:
            return
        shard_path = os.path.join(out_dir, f"shard-{len(shard_paths):05d}")
        Dataset.from_dict(pending).save_to_disk(shard_path)
        shard_paths.append(shard_path)
        for col in LOCAL_COLUMNS:
            pending[col].clear()

    for path in tqdm(files, desc="loading local files"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                row = normalize_local_row(json.loads(line))
                for col in LOCAL_COLUMNS:
                    pending[col].append(row[col])
                if len(pending["prompt"]) >= shard_rows:
                    flush()
    flush()
    if not shard_paths:
        return Dataset.from_dict({col: [] for col in LOCAL_COLUMNS})
    return concatenate_datasets([datasets.load_from_disk(path) for path in shard_paths])


def _default_column(name, ds):
    if name == "level":
        return [0] * len(ds)
    return [""] * len(ds)


def format_for_target(ds, dataset_name):
    features = TARGET_FEATURES.get(dataset_name)
    if features is None:
        return ds

    for col in features:
        if col not in ds.column_names:
            ds = ds.add_column(col, _default_column(col, ds))
    drop = [col for col in ds.column_names if col not in features]
    if drop:
        ds = ds.remove_columns(drop)
    ds = ds.select_columns(list(features))
    return ds.cast(features)


def format_split_for_target(split, dataset_name):
    return DatasetDict({k: format_for_target(v, dataset_name) for k, v in split.items()})


def load_source_dataset(source, smoke_n=0, work_dir=None):
    cache_dir = os.path.join(work_dir, "hf_cache") if work_dir else None
    if source == "staging":
        if smoke_n:
            stream = load_dataset("reasoning-core/staging", split="train", streaming=True, cache_dir=cache_dir)
            return Dataset.from_list(list(tqdm(
                stream.take(smoke_n),
                total=smoke_n,
                desc="loading staging",
            )))
        with _heartbeat("loading staging"):
            return load_dataset("reasoning-core/staging", split="train", cache_dir=cache_dir)

    path = resolve_local_source(source)
    files = local_jsonl_files(path)
    print(f"  local source: {path}", flush=True)
    print(f"  jsonl files: {len(files):,}", flush=True)
    if smoke_n:
        files = files[:max(1, min(len(files), smoke_n))]
        print(f"  smoke files: {len(files):,}", flush=True)
        stream = load_dataset("json", data_files=files, split="train", streaming=True, cache_dir=cache_dir)
        ds = Dataset.from_list(list(tqdm(
            stream.take(smoke_n),
            total=smoke_n,
            desc="loading local",
        )))
    else:
        shard_dir = os.path.join(work_dir or f"{base}/tmp/rc_preprocess_upload", "local_load")
        ds = load_local_jsonl_sharded(files, shard_dir)
    return normalize_columns(ds)

def _safe_score(cand, row, timeout=2):
    global _SCORE_DEVNULL

    def _handler(signum, frame):
        raise _Timeout()
    if _SCORE_DEVNULL is None or _SCORE_DEVNULL.closed:
        _SCORE_DEVNULL = open(os.devnull, "w")
    old = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        with contextlib.redirect_stderr(_SCORE_DEVNULL):
            return score_answer(cand, edict(row))
    except Exception:
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def build_verification(
    batch,
    pools,
    max_tries=2,
    score_timeout=1.0,
    negative_strategy="scored_same_task",
    retrieval_candidates=None,
):
    prompts, answers, modes = [], [], []
    for i, (prompt, ans, task) in enumerate(zip(batch["prompt"], batch["answer"], batch["task"])):
        pool = pools.get(task, [])
        candidates = retrieval_candidates[i] if retrieval_candidates is not None else None
        chosen, label = ans, "Yes"
        if random.random() < 0.5:
            row = {k: batch[k][i] for k in batch}
            if candidates:
                for cand in candidates[:max_tries]:
                    if cand == ans:
                        continue
                    if negative_strategy == "same_task":
                        chosen, label = cand, "No"; break
                    score = _safe_score(cand, row, timeout=score_timeout)
                    if score is not None and score != 1:
                        chosen, label = cand, "No"; break
            if label == "Yes" and negative_strategy == "same_task" and len(pool) >= 2:
                for cand in random.sample(pool, min(max_tries, len(pool))):
                    if cand != ans:
                        chosen, label = cand, "No"; break
            elif label == "Yes" and negative_strategy == "scored_same_task" and len(pool) >= 2:
                for cand in random.sample(pool, min(max_tries, len(pool))):
                    if cand == ans: continue
                    score = _safe_score(cand, row, timeout=score_timeout)
                    if score is not None and score != 1:
                        chosen, label = cand, "No"; break
        prompts.append(f"{prompt}\nAnswer:\n{chosen}\nCorrect? (Yes/No)")
        answers.append(label); modes.append("verification")
    return {"prompt": prompts, "answer": answers, "mode": modes}


def _init_verif_worker(pools, max_tries, score_timeout, negative_strategy):
    global _WORKER_POOLS, _WORKER_MAX_TRIES, _WORKER_SCORE_TIMEOUT, _WORKER_NEGATIVE_STRATEGY
    _WORKER_POOLS = pools
    _WORKER_MAX_TRIES = max_tries
    _WORKER_SCORE_TIMEOUT = score_timeout
    _WORKER_NEGATIVE_STRATEGY = negative_strategy
    random.seed(os.getpid() ^ int(time.time() * 1e6))
    # Import task modules before SIGALRM-based scoring starts; otherwise alarms
    # can interrupt importlib cleanup and produce noisy "Exception ignored" logs.
    try:
        from reasoning_core import DATASETS, match_task_name
        for task in pools:
            try:
                _ = DATASETS[match_task_name(task)]._resolved
            except Exception:
                pass
    except Exception:
        pass


def _build_verification_one(row):
    prompt, ans, task = row["prompt"], row["answer"], row["task"]
    pool = _WORKER_POOLS.get(task, [])
    candidates = row.get("_retrieval_candidates")
    score_row = {k: v for k, v in row.items() if not k.startswith("_")}
    chosen, label = ans, "Yes"
    if random.random() < 0.5 and len(pool) >= 2:
        if candidates:
            for cand in candidates[:_WORKER_MAX_TRIES]:
                if cand == ans:
                    continue
                if _WORKER_NEGATIVE_STRATEGY == "same_task":
                    chosen, label = cand, "No"; break
                score = _safe_score(cand, score_row, timeout=_WORKER_SCORE_TIMEOUT)
                if score is not None and score != 1:
                    chosen, label = cand, "No"; break
        if label == "Yes" and _WORKER_NEGATIVE_STRATEGY == "same_task":
            for cand in random.sample(pool, min(_WORKER_MAX_TRIES, len(pool))):
                if cand != ans:
                    chosen, label = cand, "No"; break
        elif label == "Yes":
            for cand in random.sample(pool, min(_WORKER_MAX_TRIES, len(pool))):
                if cand == ans:
                    continue
                score = _safe_score(cand, score_row, timeout=_WORKER_SCORE_TIMEOUT)
                if score is not None and score != 1:
                    chosen, label = cand, "No"; break
    return f"{prompt}\nAnswer:\n{chosen}\nCorrect? (Yes/No)", label, "verification"


def build_verification_parallel(
    batch,
    pools,
    workers,
    pool=None,
    max_tries=2,
    score_timeout=1.0,
    negative_strategy="scored_same_task",
    chunksize=32,
    distractor_retriever=None,
):
    rows = [{k: batch[k][i] for k in batch} for i in range(len(batch["prompt"]))]
    if distractor_retriever is not None:
        retrieval_candidates = distractor_retriever.batch_candidates(
            rows,
            k=max_tries,
            rng=os.getpid() ^ int(time.time() * 1e6),
        )
        for row, candidates in zip(rows, retrieval_candidates):
            row["_retrieval_candidates"] = candidates
    if workers <= 1:
        return build_verification(
            batch,
            pools,
            max_tries=max_tries,
            score_timeout=score_timeout,
            negative_strategy=negative_strategy,
            retrieval_candidates=[row.get("_retrieval_candidates") for row in rows],
        )
    if pool is None:
        with mp.Pool(
            processes=workers,
            initializer=_init_verif_worker,
            initargs=(pools, max_tries, score_timeout, negative_strategy),
            maxtasksperchild=1000,
        ) as local_pool:
            triples = list(local_pool.imap(_build_verification_one, rows, chunksize=chunksize))
    else:
        triples = list(pool.imap(_build_verification_one, rows, chunksize=chunksize))
    prompts, answers, modes = map(list, zip(*triples)) if triples else ([], [], [])
    return {"prompt": prompts, "answer": answers, "mode": modes}


def build_answer_pools(ds, max_per_task=8192, seed=42):
    import xxhash

    if max_per_task <= 0:
        unique = {}
        for rb in _logical_batches(ds, ["task", "answer"]):
            for task, answer in zip(rb.column("task").to_pylist(), rb.column("answer").to_pylist()):
                unique.setdefault(task, {}).setdefault(answer, None)
        return {task: list(answers) for task, answers in unique.items()}

    heaps = {}
    selected = {}
    for rb in _logical_batches(ds, ["task", "answer"]):
        tasks = rb.column("task").to_pylist()
        answers = rb.column("answer").to_pylist()
        for task, answer in zip(tasks, answers):
            chosen = selected.setdefault(task, set())
            if answer in chosen:
                continue
            h = xxhash.xxh64(str(answer).encode(), seed=seed).intdigest()
            heap = heaps.setdefault(task, [])
            item = (-h, answer)
            if len(heap) < max_per_task:
                heapq.heappush(heap, item)
                chosen.add(answer)
            elif h < -heap[0][0]:
                _, dropped = heapq.heapreplace(heap, item)
                chosen.remove(dropped)
                chosen.add(answer)

    return {task: [answer for _, answer in heap] for task, heap in heaps.items()}


def build_verification_split_sharded(
    ds_verif,
    raw_pools,
    out_dir,
    batch_size=512,
    shard_rows=100_000,
    workers=1,
    max_tries=2,
    score_timeout=1.0,
    negative_strategy="scored_same_task",
    chunksize=32,
    distractor_retriever=None,
):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    shard_paths = []
    pending = {col: [] for col in ds_verif.column_names}
    pending_rows = 0

    def flush():
        nonlocal pending, pending_rows
        if pending_rows == 0:
            return
        shard_path = os.path.join(out_dir, f"shard-{len(shard_paths):05d}")
        Dataset.from_dict(pending, features=ds_verif.features).save_to_disk(shard_path)
        shard_paths.append(shard_path)
        pending = {col: [] for col in ds_verif.column_names}
        pending_rows = 0

    pool = None
    try:
        if workers > 1:
            pool = mp.Pool(
                processes=workers,
                initializer=_init_verif_worker,
                initargs=(raw_pools, max_tries, score_timeout, negative_strategy),
                maxtasksperchild=1000,
            )
        for start in tqdm(range(0, len(ds_verif), batch_size), desc="verif"):
            batch = {k: ds_verif[start:start + batch_size][k] for k in ds_verif.column_names}
            out = build_verification_parallel(
                batch,
                raw_pools,
                workers=workers,
                pool=pool,
                max_tries=max_tries,
                score_timeout=score_timeout,
                negative_strategy=negative_strategy,
                chunksize=chunksize,
                distractor_retriever=distractor_retriever,
            )
            for col in ds_verif.column_names:
                pending[col].extend(out[col] if col in out else batch[col])
            pending_rows += len(batch["prompt"])
            if pending_rows >= shard_rows:
                flush()
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    flush()
    if not shard_paths:
        return ds_verif.select([])
    return concatenate_datasets([datasets.load_from_disk(path) for path in shard_paths])


def inject_cot(ds, ratio=0.0):
    if ratio <= 0:
        return ds

    def get_cot(x):
        if x["mode"] == "verification":
            return None
        cot = x.get("cot") or _metadata_obj(x["metadata"]).get("cot")
        return str(cot) if cot is not None and str(cot).strip() else None

    elig = ds.filter(lambda x: get_cot(x) is not None).shuffle(seed=42)
    k = int(len(elig) * ratio)
    cotted = elig.select(range(k)).map(lambda x: {
        "prompt": f"/trace {x['prompt']}",
        "answer": f"<trace>\n{get_cot(x)}\n</trace>\n{x['answer']}",
        "mode": "cot"
    })
    return concatenate_datasets([
        ds.filter(lambda x: get_cot(x) is None),
        elig.select(range(k, len(elig))), cotted
    ]).shuffle(seed=42)


def inject_fs(ds, ratio=0.07, n_shots=1, max_len=1024, seed=0, cands=32, batch_size=2048):
    rng, n, table = np.random.default_rng(seed), len(ds), ds.data.table
    idx = getattr(ds, "_indices", None)
    d2p = np.asarray(idx.column(0).to_numpy(zero_copy_only=False), dtype=np.int64) if idx else None

    def _toks():
        col, out, off = table.column("metadata"), np.empty(table.num_rows, dtype=np.int64), 0
        for chunk in tqdm(col.chunks, desc="token counts", leave=False):
            s = pl.from_arrow(chunk)
            vals = (s.str.extract(r'"_prompt_tokens"\s*:\s*(\d+)', 1).cast(pl.Int64, strict=False)
                  + s.str.extract(r'"_answer_tokens"\s*:\s*(\d+)', 1).cast(pl.Int64, strict=False)
                   ).fill_null(max_len + 1)
            out[off:off+len(chunk)] = vals.to_numpy(); off += len(chunk)
        return out

    toks_p = _toks()
    toks = toks_p if d2p is None else toks_p[d2p]
    small = table.select(["task", "mode"])
    if d2p is not None: small = small.take(pa.array(d2p))
    df = pl.from_arrow(small).with_row_index("_i")
    shot_df = df.filter(pl.col("mode") == "instruct")
    pool = {t: np.asarray(ix, dtype=np.int64)
            for t, ix in shot_df.group_by("task").agg(pl.col("_i")).iter_rows()}

    elig = rng.permutation(shot_df["_i"].to_numpy())
    pick = np.sort(elig[:int(len(elig) * ratio)])
    if not len(pick): return ds

    mask = np.zeros(n, dtype=bool); mask[pick] = True
    pc_col, ac_col = table.column("prompt"), table.column("answer")
    phys = lambda i: int(i if d2p is None else d2p[i])

    def shots(t, si, budget):
        p = pool.get(t)
        if p is None or budget <= 0: return ""
        keep, used = [], 0
        for j in map(int, rng.choice(p, size=min(cands, len(p)), replace=False)):
            if j == si or used + toks[j] > budget: continue
            keep.append(j); used += toks[j]
            if len(keep) == n_shots: break
        return "".join(f"{pc_col[phys(j)].as_py()}\nAnswer:\n{ac_col[phys(j)].as_py()}\n\n" for j in keep)

    def transform(b):
        out = {k: list(v) for k, v in b.items()}
        for i, si in enumerate(map(int, b["_fs_i"])):
            s = shots(b["task"][i], si, max_len - toks[si] - 24)
            if s: out["prompt"][i] = s + b["prompt"][i] + "\nAnswer:\n"; out["mode"][i] = "few_shot"
        return out

    fs = (ds.select(pick).add_column("_fs_i", pick)
            .map(transform, batched=True, batch_size=batch_size, desc="few-shot")
            .remove_columns(["_fs_i"]))
    return concatenate_datasets([ds.select(np.flatnonzero(~mask)), fs])


def notify(subject, body=""):
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("email skipped: RESEND_API_KEY is not set")
        return
    try:
        import resend
        resend.api_key = api_key
        resend.Emails.send({"from": "onboarding@resend.dev", "to": "damien.sileo@gmail.com",
                            "subject": subject, "html": f"<p>{html.escape(body)}</p>"})
    except Exception as e:
        print(f"email failed: {e}")


def print_yes_rate_warnings(ds_verif, tasks):
    stats = {}
    for rb in _logical_batches(ds_verif, ["task", "answer"]):
        for task, answer in zip(rb.column("task").to_pylist(), rb.column("answer").to_pylist()):
            n, yes = stats.get(task, (0, 0))
            stats[task] = (n + 1, yes + (answer == "Yes"))
    rates = {task: yes / n for task, (n, yes) in stats.items() if n}
    for task in sorted(tasks):
        yr = rates.get(task)
        if yr is not None and abs(yr - 0.5) >= 0.15:
            print(f"  WARN {task}: yes_rate={yr:.2f}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="staging",
                    help="'staging' for reasoning-core/staging, a generated_data key like rg3, or a local .jsonl file/directory")
    ap.add_argument("--dataset_name", default=None,
                    help="Output dataset name under reasoning-core; inferred from --source when omitted")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--dry_run", action="store_true")
    ap.add_argument("--smoke_test", type=int, default=0, metavar="N",
                    help="Smoke-test: stream N examples, skip upload, print timings")
    ap.add_argument("--answer_pool_max_per_task", type=int, default=8192,
                    help="Max unique candidate answers kept per task for verification; <=0 keeps all")
    ap.add_argument("--verif_batch_size", type=int, default=512)
    ap.add_argument("--verif_shard_rows", type=int, default=25_000)
    ap.add_argument("--verif_workers", type=int, default=int(os.environ.get("RC_VERIF_WORKERS", "6")),
                    help="Process workers for scored verification negatives")
    ap.add_argument("--verif_chunksize", type=int, default=32,
                    help="Rows per multiprocessing dispatch chunk")
    ap.add_argument("--verif_max_tries", type=int, default=2,
                    help="Candidate answers tried per negative row")
    ap.add_argument("--score_timeout", type=float, default=1.0,
                    help="Wall-clock seconds per candidate scorer call")
    ap.add_argument("--verif_negative_strategy", choices=["same_task", "scored_same_task"],
                    default="scored_same_task",
                    help="same_task is fast; scored_same_task is slower but filters accidental correct negatives")
    ap.add_argument("--few_shot_ratio", type=float, default=0.07,
                    help="Fraction of eligible instruct rows converted to few-shot")
    ap.add_argument("--cot_ratio", type=float, default=0.0,
                    help="Fraction of eligible instruct rows converted to CoT")
    ap.add_argument("--retrieval_min_distractors", type=int, default=10,
                    help="Use lexical distractor retrieval only for tasks with more than this many candidate answers")
    ap.add_argument("--retrieval_radius", type=int, default=0,
                    help="SimHash Hamming radius for lexical distractor retrieval buckets")
    ap.add_argument("--retrieval_query_max_chars", type=int, default=128,
                    help="Max prompt chars used as a lexical retrieval key; <=0 uses full prompt")
    ap.add_argument("--disable_distractor_retrieval", action="store_true",
                    help="Keep the original random same-task distractor sampling path")
    ap.add_argument("--work_dir", default=f"{tmp_root}/rc_preprocess_upload",
                    help="Parent directory for temporary on-disk shards")
    ap.add_argument("--keep_work_dir", action="store_true",
                    help="Keep this run's temporary shards for debugging")
    args = ap.parse_args()
    args.dataset_name = args.dataset_name or infer_dataset_name(args.source)

    global _RUN_DIR, _KEEP_WORK_DIR
    os.makedirs(args.work_dir, exist_ok=True)
    _RUN_DIR = tempfile.mkdtemp(prefix="run-", dir=args.work_dir)
    _KEEP_WORK_DIR = args.keep_work_dir
    args.work_dir = _RUN_DIR

    smoke = args.smoke_test > 0
    if smoke:
        args.dry_run = True
        print(f"=== SMOKE TEST ({args.smoke_test:,} examples, no upload) ===")
    print(f"source: {args.source}", flush=True)
    print(f"name: {os.path.basename(args.source.rstrip('/'))} -> {args.dataset_name}", flush=True)
    print(f"output: reasoning-core/{args.dataset_name}", flush=True)
    print(f"work dir: {args.work_dir}", flush=True)

    with _step(f"loading {args.source}"):
        ds = load_source_dataset(args.source, smoke_n=args.smoke_test if smoke else 0, work_dir=args.work_dir)
        print(f"  {len(ds):,} rows")
        if len(ds) == 0:
            raise RuntimeError(f"{args.source} returned 0 rows")

    with _step("deduplicating"):
        ds, rep = deduplicate_by_column(ds)
        print(f"  {rep}")

    task_counts = count_by_column(ds, key="task")
    if args.source == "staging":
        missing = set(list_tasks()) - set(task_counts)
        if missing: print(f"  missing tasks: {missing}")

    with _step("subsampling"):
        ds = subsample(ds, top_k=max(1, len(task_counts) - 6))

    sample_n = min(50_000, len(ds))
    sample_tokens = sum(_token_count(x["metadata"]) for x in ds.select(range(sample_n)))
    n_tok = sample_tokens / 1e9 * len(ds) / max(sample_n, 1)
    print(f"  ~{n_tok:.2f}B tokens | {len(ds):,} rows")

    with _step("filter long prompts"):
        ds = filter_by_string_length(ds, "prompt", 50_000)
        print(f"  {len(ds):,} rows")
        if len(ds) < 2:
            raise RuntimeError("fewer than 2 rows remain after filtering")

    with _step("split train/verif"):
        spl = ds.train_test_split(test_size=0.125, seed=42)
        ds_std, ds_verif = spl["train"], spl["test"]
        print(f"  train={len(ds_std):,} verif={len(ds_verif):,}")

    with _step("build answer pools"):
        raw_pools = build_answer_pools(ds, max_per_task=args.answer_pool_max_per_task)
        total_candidates = sum(len(v) for v in raw_pools.values())
        capped = "" if args.answer_pool_max_per_task <= 0 else f" (cap={args.answer_pool_max_per_task:,}/task)"
        print(f"  {total_candidates:,} candidates across {len(raw_pools)} tasks{capped}")

    distractor_retriever = None
    if not args.disable_distractor_retrieval:
        with _step("build distractor retrieval"):
            distractor_retriever = VerificationDistractorRetriever.from_pools(
                raw_pools,
                min_distractors=args.retrieval_min_distractors,
                radius=args.retrieval_radius,
                query_max_chars=args.retrieval_query_max_chars,
            )
            stats = distractor_retriever.stats()
            print(
                f"  {stats['n_candidates']:,} indexed candidates across {stats['n_tasks']} tasks; "
                f"{stats['eligible_tasks']} tasks have >{args.retrieval_min_distractors} candidates"
            )

    with _step("build verification split"):
        # Iterate in main process to avoid forked subprocesses around SIGALRM.
        shard_dir = os.path.join(args.work_dir, "verification")
        ds_verif = build_verification_split_sharded(
            ds_verif,
            raw_pools,
            shard_dir,
            batch_size=args.verif_batch_size,
            shard_rows=args.verif_shard_rows,
            workers=args.verif_workers,
            max_tries=args.verif_max_tries,
            score_timeout=args.score_timeout,
            negative_strategy=args.verif_negative_strategy,
            chunksize=args.verif_chunksize,
            distractor_retriever=distractor_retriever,
        )

    print_yes_rate_warnings(ds_verif, raw_pools)

    with _step("concat + subsample"):
        ds = concatenate_datasets([ds_std, ds_verif])
        if args.dataset_name == "reasoning-gym":
            print("  skipping final task balancing for reasoning-gym")
        else:
            ds = subsample(ds, top_k=len(count_by_column(ds, key="task")) // 2)

    with _step("inject CoT"):
        ds = inject_cot(ds, ratio=args.cot_ratio)

    with _step("inject few-shot"):
        ds = inject_fs(ds, ratio=args.few_shot_ratio)

    with _step("final split + prettyorder"):
        test_size = max(1, int(len(ds) * 0.01)) if len(ds) > 1 else 0
        split = ds.train_test_split(test_size=test_size, seed=42) if test_size else DatasetDict({"train": ds})
        split = DatasetDict({k: prettyorder_low_memory(v, ["task", "mode"]) for k, v in split.items()})
        split = format_split_for_target(split, args.dataset_name)
        print(split)

    if args.dry_run:
        print("\n[no upload]")
    else:
        with _step(f"push to reasoning-core/{args.dataset_name}"):
            split.push_to_hub(f"reasoning-core/{args.dataset_name}", private=args.private)
        notify(f"✅ RC preprocess done — {n_tok:.1f}B tokens",
               f"{len(split['train']):,} train rows pushed to reasoning-core/{args.dataset_name}")

    total = sum(_timings.values())
    print("\n── timings ──")
    for k, v in _timings.items():
        print(f"  {k:<35} {v:6.1f}s  ({v/total*100:.0f}%)")
    print(f"  {'TOTAL':<35} {total:6.1f}s")
    if smoke:
        if args.smoke_test >= 10_000:
            scale = 13_700_000 / args.smoke_test
            print(f"\n  (scaled to full ~{total*scale/3600:.1f}h estimate, "
                  f"excl. verif which scales sub-linearly with scoring)")
        else:
            print("\n  (smoke sample too small for a useful full-run time estimate)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        tb = traceback.format_exc()
        print(tb, file=sys.stderr, flush=True)
        notify(f"❌ RC preprocess failed: {type(e).__name__}", tb[-8000:])
        raise
    finally:
        _cleanup_work_dir()
