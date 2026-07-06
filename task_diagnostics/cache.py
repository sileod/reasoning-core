"""cache.py — build & load the canonical local task-row cache.

Generation happens ONLY in `build` (explicit), NEVER at analysis time. Analyses call load_task_rows()
and consume immutable rows, so nothing silently regenerates or mixes versions. Storage = Parquet shards
+ manifest.json, so the same rows round-trip through a local dir OR a Hugging Face repo revision.

    python -m task_diagnostics.cache build --tasks logic_nli arithmetics --levels 0 1 2 --n 64
    load_task_rows(path="task_diagnostics/cache/task_rows/<id>")          # local fresh cache
    load_task_rows(repo="reasoning-core/procedural-pretraining-pile", revision="<sha>")  # pinned pile
"""
from __future__ import annotations
from concurrent.futures.process import BrokenProcessPool
import hashlib
import inspect
import json
import subprocess
from pathlib import Path

import reasoning_core as rc

try:
    from .schemas import TaskRow, CacheManifest, canonical_json
except ImportError:                    # script / bare-name run (task_diagnostics/ on sys.path)
    from schemas import TaskRow, CacheManifest, canonical_json

DEFAULT_OUT = "task_diagnostics/cache/task_rows"

# ── reference tokenizer (for length signal; model-agnostic cache pins ONE ref tokenizer) ──
_TOK = None
def _ref_tok():
    global _TOK
    if _TOK is None:
        try:
            from transformers import AutoTokenizer
            _TOK = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M")
        except Exception:
            _TOK = False
    return _TOK
def _ntok(s: str) -> int:
    tk = _ref_tok()
    try:
        return len(tk(s, add_special_tokens=False).input_ids) if tk else -1
    except Exception:
        return -1

def _task_obj(name):
    T = rc.get_task(name)
    return T() if isinstance(T, type) else T

def _behavior_hash(t):
    bh = getattr(t, "behavior_hash", "?")
    return bh() if callable(bh) else bh

def _generator_commit() -> str:
    try:
        root = Path(__file__).resolve().parents[1]
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return ""

def _task_source(t) -> str:
    try:
        return inspect.getsource(t if inspect.isclass(t) else t.__class__)
    except Exception:
        return ""

def _source_hash(source: str) -> str:
    return hashlib.sha1(source.encode()).hexdigest()[:16] if source else ""

def _generate_batch(task, n, level, workers):
    try:
        return task.generate_balanced_batch(batch_size=n, level=level, deduplication=True,
                                            workers=workers)
    except BrokenProcessPool:
        return task.generate_balanced_batch(batch_size=n, level=level, deduplication=True,
                                            workers=1)

def _cache_id(tasks, levels, n, mode, gen_ver, bhashes, task_versions, configs) -> str:
    key = json.dumps({"tasks": sorted(tasks), "levels": sorted(levels), "n": n, "mode": mode,
                      "gen": gen_ver, "bh": bhashes, "versions": task_versions,
                      "configs": configs}, sort_keys=True)
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def _hf_cache_id(repo, revision, tasks, levels, n, mode) -> str:
    key = json.dumps({"repo": repo, "revision": revision, "tasks": sorted(tasks),
                      "levels": sorted(levels), "n": n, "mode": mode}, sort_keys=True)
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def _metadata_dict(x):
    md = x.get("metadata", {}) or {}
    if isinstance(md, str):
        try:
            md = json.loads(md)
        except Exception:
            md = {}
    return md


def _task_spec(name):
    task = _task_obj(name)
    cfg = getattr(task, "config", None)
    return {
        "behavior_hash": _behavior_hash(task),
        "task_version": str(getattr(task, "task_version", getattr(task, "version", "0"))),
        "config": canonical_json(cfg.to_dict() if hasattr(cfg, "to_dict")
                                 else getattr(cfg, "__dict__", {}) or {}),
    }


def cached_task_specs(out_dir=DEFAULT_OUT, levels=(0, 1, 2, 3, 4), n_per_task=64,
                      mode="instruct"):
    """task -> current cache spec for manifests matching this sampling request."""
    out, specs = Path(out_dir), {}
    for mf in out.glob("*/manifest.json"):
        try:
            m = json.loads(mf.read_text())
        except Exception:
            continue
        if tuple(m.get("levels", ())) != tuple(levels):
            continue
        if m.get("n_per_task") != n_per_task or m.get("mode") != mode:
            continue
        for task in m.get("tasks", ()):
            if task in m.get("behavior_hashes", {}):
                specs[task] = {
                    "behavior_hash": m["behavior_hashes"].get(task),
                    "task_version": str(m.get("task_versions", {}).get(task, "0")),
                    "config": m.get("configs", {}).get(task, "{}"),
                }
    return specs


def changed_tasks(tasks=None, levels=(0, 1, 2, 3, 4), n_per_task=64,
                  out_dir=DEFAULT_OUT, mode="instruct"):
    """Tasks without a matching current cache for this sampling request."""
    tasks = list(tasks or rc.list_tasks())
    cached = cached_task_specs(out_dir, levels, n_per_task, mode)
    return [t for t in tasks if cached.get(t) != _task_spec(t)]


def _write_cache(rows, manifest, out_dir=DEFAULT_OUT, analyze=True):
    if not rows:
        raise RuntimeError("no rows produced for cache")
    out = Path(out_dir) / manifest.cache_id
    (out / "data").mkdir(parents=True, exist_ok=True)
    import pandas as pd
    df = pd.DataFrame([r.to_dict() for r in rows]).drop_duplicates("row_hash")
    df.to_parquet(out / "data" / "part-00000.parquet", index=False)
    manifest = CacheManifest(**{**manifest.to_dict(), "n_rows": len(df)})
    (out / "manifest.json").write_text(json.dumps(manifest.to_dict(), indent=2))
    if analyze:
        _write_analysis(df, out)
    return manifest, out


def build_task_cache(tasks, levels=(0, 1, 2, 3, 4), n_per_task=64,
                     out_dir=DEFAULT_OUT, mode="instruct", analyze=True, workers=1):
    """Generate rows for each (task, level), write Parquet + manifest, and (default) an analysis summary.
    cache_id keys on behavior_hash + task_version + config + levels + n + mode (Codex/claude review)."""
    tasks, levels = list(tasks), list(levels)
    gen_ver = str(getattr(rc, "__version__", "0"))
    rows, bhashes, task_versions, configs, sources, source_hashes = [], {}, {}, {}, {}, {}
    for name in tasks:
        t = _task_obj(name)
        bhashes[name] = _behavior_hash(t)
        task_versions[name] = str(getattr(t, "task_version", getattr(t, "version", "0")))
        cfg = getattr(t, "config", None)
        configs[name] = canonical_json(cfg.to_dict() if hasattr(cfg, "to_dict")
                                       else getattr(cfg, "__dict__", {}) or {})
        sources[name] = _task_source(t)
        source_hashes[name] = _source_hash(sources[name])
        for lvl in levels:
            for ex in _generate_batch(t, n_per_task, lvl, workers):
                d = ex.to_dict()
                md = canonical_json(d.get("metadata", "{}"))
                try:
                    alvl = int(json.loads(md).get("_level", lvl))
                except Exception:
                    alvl = lvl
                prompt, answer = d.get("prompt", ""), str(d.get("answer", ""))
                meta = _metadata_dict({"metadata": md})
                rows.append(TaskRow(
                    task=name, level=alvl, prompt=prompt, answer=answer, metadata=md, mode=mode,
                    task_version=task_versions[name], behavior_hash=bhashes[name], config=configs[name],
                    prompt_tokens=int(meta.get("_prompt_tokens", _ntok(prompt))),
                    answer_tokens=int(meta.get("_answer_tokens", _ntok(answer))),
                    gen_time_s=round(float(meta.get("_time", -1)), 5),
                    row_hash=TaskRow.compute_hash(name, alvl, prompt, answer, md)))

    cid = _cache_id(tasks, levels, n_per_task, mode, gen_ver, bhashes, task_versions, configs)
    man = CacheManifest(cache_id=cid, source="fresh", tasks=tuple(tasks), levels=tuple(levels),
                        n_per_task=n_per_task, mode=mode, generator_version=gen_ver,
                        behavior_hashes=bhashes, task_versions=task_versions, configs=configs,
                        tokenizer="HuggingFaceTB/SmolLM2-135M",
                        generator_commit=_generator_commit(), sources=sources,
                        source_hashes=source_hashes)
    return _write_cache(rows, man, out_dir, analyze)


def import_hf_cache(repo, revision=None, tasks=None, levels=None, n_per_task=64,
                    out_dir=DEFAULT_OUT, mode="instruct", scan_cap=500_000, analyze=True):
    """Stream an HF pile into the same local TaskRow Parquet cache used by diagnostics."""
    from datasets import load_dataset
    tasks = set(tasks or [])
    levels = tuple(levels) if levels is not None else ()
    wanted_levels = {int(x) for x in levels} if levels else None
    rows, counts, scanned, generator_commits = [], {}, 0, set()
    for x in load_dataset(repo, revision=revision, split="train", streaming=True):
        scanned += 1
        task = (x.get("task") or "").strip()
        prompt = x.get("prompt") or x.get("question") or ""
        answer = x.get("answer")
        if not task or not prompt or answer is None or (tasks and task not in tasks):
            continue
        md = _metadata_dict(x)
        if md.get("_generator_commit") or x.get("generator_commit"):
            generator_commits.add(md.get("_generator_commit") or x.get("generator_commit"))
        level = x.get("level", md.get("_level", 0))
        try:
            level = int(level)
        except Exception:
            level = 0
        if wanted_levels is not None and level not in wanted_levels:
            continue
        key = (task, level)
        if counts.get(key, 0) >= n_per_task:
            continue
        metadata = canonical_json(md or x.get("metadata", {}))
        task_version = str(x.get("task_version", md.get("_task_version", "0")))
        behavior_hash = x.get("behavior_hash", md.get("_task_behavior_hash", "?"))
        config = canonical_json(x.get("config", md.get("_config", {})))
        row_mode = x.get("mode") or mode
        rows.append(TaskRow(
            task=task, level=level, prompt=prompt, answer=str(answer), metadata=metadata,
            mode=row_mode, task_version=task_version, behavior_hash=behavior_hash,
            config=config,
            prompt_tokens=int(x.get("prompt_tokens", md.get("_prompt_tokens", _ntok(prompt))) or -1),
            answer_tokens=int(x.get("answer_tokens", md.get("_answer_tokens", _ntok(str(answer)))) or -1),
            gen_time_s=float(x.get("gen_time_s", md.get("_time", -1)) or -1),
            row_hash=x.get("row_hash") or TaskRow.compute_hash(task, level, prompt, str(answer), metadata),
        ))
        counts[key] = counts.get(key, 0) + 1
        if scanned >= scan_cap:
            break
    task_names = sorted({r.task for r in rows})
    bhashes = {t: next((r.behavior_hash for r in rows if r.task == t), "?") for t in task_names}
    versions = {t: next((r.task_version for r in rows if r.task == t), "0") for t in task_names}
    configs = {t: next((r.config for r in rows if r.task == t), "{}") for t in task_names}
    cache_levels = tuple(sorted({r.level for r in rows}))
    cid = _hf_cache_id(repo, revision, task_names, cache_levels, n_per_task, mode)
    man = CacheManifest(cache_id=cid, source="hf", tasks=tuple(task_names), levels=cache_levels,
                        n_per_task=n_per_task, mode=mode, generator_version=str(getattr(rc, "__version__", "0")),
                        behavior_hashes=bhashes, task_versions=versions, configs=configs,
                        tokenizer="HuggingFaceTB/SmolLM2-135M",
                        generator_commit=sorted(generator_commits)[0] if generator_commits else "",
                        sources={}, source_hashes={}, repo=repo, revision=revision)
    return _write_cache(rows, man, out_dir, analyze)


def _write_analysis(df, out):
    import statistics as st
    lines = [f"# cache {out.name} — {len(df)} rows, {df.task.nunique() if len(df) else 0} tasks", "",
             "## generation speed per (task, level)  [ms/example]", ""]
    timed = df[df.gen_time_s >= 0] if len(df) and "gen_time_s" in df else df.iloc[:0]
    for (task, lvl), grp in timed.groupby(["task", "level"]):
        ts = list(grp.gen_time_s)
        lines.append(f"  {task:<28} L{lvl}: {st.mean(ts) * 1000:6.1f}ms  n={len(ts)}")
    total = len(df)
    lines.append(f"\ndup rate (row_hash): {1 - len(df.row_hash.unique()) / max(total, 1):.1%}" if len(df) else "\ndup rate (row_hash): n/a")
    (out / "analysis.md").write_text("\n".join(lines))
    print("\n".join(lines))


def load_task_rows(path=None, repo=None, revision=None, tasks=None, levels=None, n_per_task=None):
    """Immutable row iterator. Local Parquet (path=) OR a pinned HF repo (repo=, revision=). NEVER
    generates. Tolerates HF-pile rows that lack cache-only fields (fills sensible defaults)."""
    import pandas as pd
    if path:
        files = sorted(Path(path).glob("**/*.parquet"))
        if not files:
            raise FileNotFoundError(f"no parquet under {path}")
        df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    elif repo:
        from datasets import load_dataset
        df = load_dataset(repo, revision=revision, split="train").to_pandas()
    else:
        raise ValueError("load_task_rows needs path= or repo=")
    if tasks:
        df = df[df["task"].isin(list(tasks))]
    if levels is not None and "level" in df:
        df = df[df["level"].isin(list(levels))]
    if n_per_task:
        df = df.groupby("task", group_keys=False).head(n_per_task)
    for _, r in df.iterrows():
        d = r.to_dict()
        md = canonical_json(d.get("metadata", "{}"))
        yield TaskRow(
            task=d.get("task"), level=int(d.get("level") or 0), prompt=d.get("prompt", ""),
            answer=str(d.get("answer", "")), metadata=md, mode=d.get("mode", "instruct"),
            task_version=str(d.get("task_version", "0")), behavior_hash=d.get("behavior_hash", "?"),
            config=d["config"] if isinstance(d.get("config"), str) else canonical_json(d.get("config", "{}")),
            prompt_tokens=int(d.get("prompt_tokens", -1)) if d.get("prompt_tokens") is not None else -1,
            answer_tokens=int(d.get("answer_tokens", -1)) if d.get("answer_tokens") is not None else -1,
            gen_time_s=float(d.get("gen_time_s", -1) or -1),
            row_hash=d.get("row_hash") or TaskRow.compute_hash(
                d.get("task"), d.get("level", 0), d.get("prompt", ""), str(d.get("answer", "")), md))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="build/inspect the canonical task-row cache")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--tasks", nargs="+", default=None,
                   help="Tasks to build. Default: tasks changed or missing from matching caches.")
    b.add_argument("--all", action="store_true", help="Build all registered tasks.")
    b.add_argument("--levels", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    b.add_argument("--n", type=int, default=64, dest="n_per_task")
    b.add_argument("--workers", type=int, default=1,
                   help="Generator worker processes inside generate_balanced_batch.")
    b.add_argument("--out", default=DEFAULT_OUT)
    b.add_argument("--no-analyze", action="store_true")
    hf = sub.add_parser("from-hf")
    hf.add_argument("--repo", required=True, help="HF dataset repo, e.g. reasoning-core/reasoning-gym.")
    hf.add_argument("--revision", default=None)
    hf.add_argument("--tasks", nargs="+", default=None)
    hf.add_argument("--levels", nargs="+", type=int, default=None)
    hf.add_argument("--n", type=int, default=64, dest="n_per_task")
    hf.add_argument("--out", default=DEFAULT_OUT)
    hf.add_argument("--mode", default="instruct")
    hf.add_argument("--scan-cap", type=int, default=500_000)
    hf.add_argument("--no-analyze", action="store_true")
    a = ap.parse_args()
    if a.cmd == "build":
        tasks = rc.list_tasks() if a.all else (a.tasks or changed_tasks(
            levels=a.levels, n_per_task=a.n_per_task, out_dir=a.out))
        if not tasks:
            print("✅ cache fresh: no changed tasks for this sampling request")
            raise SystemExit(0)
        man, out = build_task_cache(tasks, a.levels, a.n_per_task, a.out,
                                    analyze=not a.no_analyze, workers=a.workers)
        print(f"\n✅ cache {man.cache_id}: {man.n_rows} rows → {out}")
    elif a.cmd == "from-hf":
        man, out = import_hf_cache(a.repo, a.revision, a.tasks, a.levels, a.n_per_task,
                                   a.out, a.mode, a.scan_cap, analyze=not a.no_analyze)
        print(f"\n✅ cache {man.cache_id}: {man.n_rows} rows from {a.repo} → {out}")
