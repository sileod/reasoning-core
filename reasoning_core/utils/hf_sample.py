"""A seeded uniform row sample of a pinned Hugging Face parquet dataset, cached by its spec.

Uniform over the whole split, not a prefix: tasksource-style datasets are sorted by task, so the first
N rows of a stream are a handful of tasks. The split's files are downloaded once into the HF cache;
the sample itself is written to `cache_dir/<spec hash>.parquet` and re-read on the next call.

    rows = sample_rows("tasksource/tasksource_dpo_pairs", revision, n=50_000, seed=0,
                       columns=["prompt", "chosen", "rejected", "task"])
"""
import fnmatch
import hashlib
import json
import os
import random
from pathlib import Path

CACHE_DIR = Path(os.environ.get("RC_SAMPLE_CACHE", "~/.cache/reasoning_core/samples")).expanduser()


def sample_rows(repo, revision, n, seed=0, columns=None, pattern="data/train-*.parquet",
                cache_dir=CACHE_DIR):
    """List of row dicts: `n` rows drawn without replacement, in file order, from the files matching
    `pattern` at `revision` (a full 40-char commit, so the sample never drifts with the repo)."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, hf_hub_download

    if len(str(revision)) != 40:
        raise ValueError(f"revision must be a full commit sha, got {revision!r}")
    spec = {"repo": repo, "revision": revision, "n": n, "seed": seed, "columns": columns,
            "pattern": pattern, "version": 1}
    out = Path(cache_dir) / (hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:16]
                             + ".parquet")
    if out.exists():
        return pq.read_table(out).to_pylist()

    files = sorted(f for f in HfApi().list_repo_files(repo, repo_type="dataset", revision=revision)
                   if fnmatch.fnmatch(f, pattern))
    if not files:
        raise FileNotFoundError(f"{repo}@{revision}: no files match {pattern!r}")
    paths = [hf_hub_download(repo, f, repo_type="dataset", revision=revision) for f in files]
    sizes = [pq.ParquetFile(p).metadata.num_rows for p in paths]
    picks = sorted(random.Random(seed).sample(range(sum(sizes)), min(n, sum(sizes))))

    tables, start, i = [], 0, 0
    for path, size in zip(paths, sizes):
        local = []
        while i < len(picks) and picks[i] < start + size:
            local.append(picks[i] - start)
            i += 1
        if local:
            tables.append(pq.read_table(path, columns=columns).take(local))
        start += size
    table = pa.concat_tables(tables)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(f".{os.getpid()}.tmp")
    pq.write_table(table, tmp)
    tmp.replace(out)                    # atomic: concurrent jobs never read a half-written sample
    return table.to_pylist()
