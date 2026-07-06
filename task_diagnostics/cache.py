"""cache.py — build & load the canonical local task-row cache.

Generation happens ONLY in `build` (explicit), NEVER at analysis time. Analyses call load_task_rows()
and consume immutable rows, so nothing silently regenerates or mixes versions. Storage = Parquet shards
+ manifest.json, so the same rows round-trip through a local dir OR a Hugging Face repo revision.

    python -m task_diagnostics.cache build --tasks logic_nli arithmetics --levels 0 1 2 --n 64
    load_task_rows(path="task_diagnostics/cache/task_rows/<id>")          # local fresh cache
    load_task_rows(repo="reasoning-core/procedural-pretraining-pile", revision="<sha>")  # pinned pile
"""
from __future__ import annotations
import hashlib
import json
import time
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

def _cache_id(tasks, levels, n, mode, gen_ver, bhashes) -> str:
    key = json.dumps({"tasks": sorted(tasks), "levels": sorted(levels), "n": n, "mode": mode,
                      "gen": gen_ver, "bh": bhashes}, sort_keys=True)
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def build_task_cache(tasks, levels=(0, 1, 2, 3, 4), n_per_task=64,
                     out_dir=DEFAULT_OUT, mode="instruct", analyze=True):
    """Generate rows for each (task, level), write Parquet + manifest, and (default) an analysis summary.
    cache_id keys on behavior_hash + task_version + config + levels + n + mode (Codex/claude review)."""
    tasks, levels = list(tasks), list(levels)
    gen_ver = str(getattr(rc, "__version__", "0"))
    rows, bhashes, gtime = [], {}, {}
    for name in tasks:
        t = _task_obj(name)
        bhashes[name] = _behavior_hash(t)
        tver = str(getattr(t, "version", "0"))
        cfg = canonical_json(getattr(getattr(t, "config", None), "__dict__", {}) or {})
        for lvl in levels:
            for _ in range(n_per_task):
                t0 = time.time()
                try:
                    ex = t.generate_example(level=lvl)
                except Exception:
                    continue
                dt = time.time() - t0
                d = ex.to_dict()
                md = canonical_json(d.get("metadata", "{}"))
                try:
                    alvl = int(json.loads(md).get("_level", lvl))
                except Exception:
                    alvl = lvl
                prompt, answer = d.get("prompt", ""), str(d.get("answer", ""))
                rows.append(TaskRow(
                    task=name, level=alvl, prompt=prompt, answer=answer, metadata=md, mode=mode,
                    task_version=tver, behavior_hash=bhashes[name], config=cfg,
                    prompt_tokens=_ntok(prompt), answer_tokens=_ntok(answer),
                    gen_time_s=round(dt, 5),
                    row_hash=TaskRow.compute_hash(name, alvl, prompt, answer, md)))
                gtime.setdefault((name, alvl), []).append(dt)

    cid = _cache_id(tasks, levels, n_per_task, mode, gen_ver, bhashes)
    out = Path(out_dir) / cid
    (out / "data").mkdir(parents=True, exist_ok=True)
    import pandas as pd
    df = pd.DataFrame([r.to_dict() for r in rows]).drop_duplicates("row_hash")
    df.to_parquet(out / "data" / "part-00000.parquet", index=False)
    man = CacheManifest(cache_id=cid, source="fresh", tasks=tuple(tasks), levels=tuple(levels),
                        n_per_task=n_per_task, mode=mode, generator_version=gen_ver,
                        behavior_hashes=bhashes, tokenizer="HuggingFaceTB/SmolLM2-135M", n_rows=len(df))
    (out / "manifest.json").write_text(json.dumps(man.to_dict(), indent=2))
    if analyze:
        _write_analysis(df, gtime, out)
    return man, out


def _write_analysis(df, gtime, out):
    import statistics as st
    total = sum(len(v) for v in gtime.values())
    lines = [f"# cache {out.name} — {len(df)} rows, {df.task.nunique()} tasks", "",
             "## generation speed per (task, level)  [ms/example]", ""]
    for (task, lvl), ts in sorted(gtime.items()):
        lines.append(f"  {task:<28} L{lvl}: {st.mean(ts) * 1000:6.1f}ms  n={len(ts)}")
    lines.append(f"\ndup rate (row_hash): {1 - len(df) / max(total, 1):.1%}")
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


def aux_pairs_to_rows(pairs_json_path, mode="instruct"):
    """Compat adapter: old {task: [[prompt, answer], ...]} local aux → TaskRow (level unknown = -1).
    Lets existing pair-format caches feed the new row-based analyses without a big-bang migration."""
    data = json.loads(Path(pairs_json_path).read_text())
    for task, rows in data.items():
        for r in rows:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2 and r[1]):
                continue
            p, a = r[0], str(r[1])
            yield TaskRow(task=task, level=-1, prompt=p, answer=a, metadata="{}", mode=mode,
                          task_version="0", behavior_hash="?", config="{}",
                          prompt_tokens=-1, answer_tokens=-1, gen_time_s=-1.0,
                          row_hash=TaskRow.compute_hash(task, -1, p, a, "{}"))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="build/inspect the canonical task-row cache")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--tasks", nargs="+", required=True)
    b.add_argument("--levels", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    b.add_argument("--n", type=int, default=64, dest="n_per_task")
    b.add_argument("--out", default=DEFAULT_OUT)
    b.add_argument("--no-analyze", action="store_true")
    a = ap.parse_args()
    if a.cmd == "build":
        man, out = build_task_cache(a.tasks, a.levels, a.n_per_task, a.out, analyze=not a.no_analyze)
        print(f"\n✅ cache {man.cache_id}: {man.n_rows} rows → {out}")
