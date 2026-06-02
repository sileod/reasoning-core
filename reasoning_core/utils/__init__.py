import math
import os
import tempfile
import subprocess
import json
import udocker

def score_scalar(answer, entry, k=10.0):
    import math
    """
    Scores an answer based on a unified, scaled error metric.
    This version uses a steep penalty (k=10.0) for high sensitivity.
    """
    if hasattr(entry, 'answer'):
        reference = float(entry.answer)
    else:
        reference = float(entry)
    try:
        submitted = float(str(answer).split('=')[-1].strip().rstrip('.'))
    except (ValueError, TypeError):
        return 0.0

    # Unified error: abs_err / (abs_ref + 1).
    normalized_error = abs(submitted - reference) / (abs(reference) + 1.0)

    # Exponential decay with a very strict penalty (k=10.0)
    semantic_reward = math.exp(-k * normalized_error)

    try:
        float(str(answer))
        format_reward = 1.0
    except ValueError:
        format_reward = 0.75

    return semantic_reward * format_reward


def prettyorder(ds, cols="task", n_pretty=3, seed=42, progress=True):
    from tqdm.auto import tqdm
    import random
    
    print("loading grouping columns...", flush=True)
    cols = [cols] if isinstance(cols, str) else cols
    keys = list(zip(*(ds[c] for c in cols)))
    print("building groups...", flush=True)
    groups = {}
    for i, k in tqdm(enumerate(keys), total=len(ds), disable=not progress):
        groups.setdefault(k, []).append(i)

    sorted_keys = sorted(groups)

    prefix = []
    for cycle in range(n_pretty):
        for k in sorted_keys:
            if cycle < len(groups[k]):
                prefix.append(groups[k][cycle])

    remaining = []
    for k in sorted_keys:
        remaining.extend(groups[k][n_pretty:])

    rng = random.Random(seed)
    rng.shuffle(remaining)

    indices = prefix + remaining
    print(f"🎨 prettyorder: {len(prefix)} interleaved rows "
          f"({n_pretty}×{len(sorted_keys)} groups) + "
          f"{len(remaining)} shuffled")
    return ds.select(indices)


def deduplicate_dataset(ds, column="prompt", report=True):
    import xxhash

    seen = set()
    n0 = ds.num_rows

    def is_unique(example):
        h = xxhash.xxh64_intdigest(example[column].encode())
        if h in seen:
            return False
        seen.add(h)
        return True

    ds = ds.filter(is_unique, load_from_cache_file=False, desc="deduplicating")

    if not report:
        return ds

    removed = n0 - ds.num_rows
    return ds, {
        "before": n0,
        "after": ds.num_rows,
        "removed": removed,
        "removed_pct": round(100 * removed / max(n0, 1), 2),
    }