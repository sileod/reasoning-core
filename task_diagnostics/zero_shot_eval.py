#!/usr/bin/env python
"""Zero-shot task-solvability eval via litlm + OpenRouter/NVIDIA-NIM (cheap models, ~25 ex/task).

Measures REAL free-generation reward (task.score_answer) — the honest counterpart to
teacher-forced token accuracy, which inflates on tasks a model can "follow" but not
"lead". Low reward on a capable model = genuinely hard/unlearnable.

Reproducible on ANY machine: in-repo generators + litlm. No data_cache, no GPU, no
training. Requires `pip install litlm` and a provider key in the env:
  NVIDIA_NIM_API_KEY  (default models — free NVIDIA NIM endpoints), or
  OPENROUTER_API_KEY  (for --models openrouter/...).

Storage (kept SEPARATE from the canonical task examples):
  zero_shot_preds.jsonl  — one row per (task, model, example): prompt, gold, model
                           output, extracted answer, score, ok. Source of truth.
  ZERO_SHOT.json         — aggregate reward per (task, model) + gen_time, derived.
                           (Combined report card w/ influence+saturation is rendered
                           by the diagnostics aggregator, not here.)

Examples are NON-deterministic by design (no seeding — diverse generation is the point).
Hash-cached + accumulate-to-n: predictions are keyed by a signature over the task's
behavior_hash + system + max_tokens; each run tops up to --n ok examples per (task,
model), so re-runs fill free-tier rate-limit gaps and skip once the target is met.
A changed generator (behavior_hash) invalidates old rows. Pass --refresh to recompute.

  python task_diagnostics/zero_shot_eval.py
  python task_diagnostics/zero_shot_eval.py --tasks logic_nli count_elements analogical_case_retrieval
  python task_diagnostics/zero_shot_eval.py --models nvidia_nim/nvidia/nemotron-3-super-120b-a12b --n 25

PILE / by-LEVEL hardness (rc vs rg across difficulty levels, unified score_answer, multi-model):
  python task_diagnostics/zero_shot_eval.py --datasets rc rg --n 40 --max-concurrency 1 \
      --models nvidia_nim/meta/llama-3.1-8b-instruct nvidia_nim/meta/llama-3.3-70b-instruct
  python task_diagnostics/zero_shot_eval.py --datasets rc rg --report      # by-level summary, no API
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from concurrent.futures.process import BrokenProcessPool
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reasoning_core import get_task, list_tasks  # noqa: E402
import litlm  # noqa: E402

DEFAULT_MODELS = [                                       # free NVIDIA NIM endpoint (needs NVIDIA_NIM_API_KEY)
    "nvidia_nim/meta/llama-3.1-8b-instruct",             # fast, reliable instruct — the default signal
]                                                         # plain instruct > reasoning models here (clean answers, no <think>)
# Scaling test (bigger model, same task set — does capacity solve more?): run separately, throttled,
# it accumulates into the same preds store. The free 70B tier is slow, so keep concurrency low:
#   zero_shot_eval.py --models nvidia_nim/meta/llama-3.3-70b-instruct --max-concurrency 2
SYSTEM = (
    "You are solving a reasoning task. Read the problem and reply with ONLY the final "
    "answer, in exactly the format the problem asks for — no explanation. Put the final "
    "answer inside <answer></answer> tags."
)


def _sig(behavior_hash, args):
    """Signature over what changes a prediction's MEANING (task version + eval config).
    NOT n/seed: examples are non-deterministic by design; n is a target we accumulate to."""
    payload = json.dumps({"bh": behavior_hash, "sys": args.system,
                          "max_tokens": args.max_tokens}, sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


def _row_sig(args):
    """Eval signature for immutable TaskRow caches. Row identity/version is in row_hash."""
    payload = json.dumps({"row_schema": "TaskRow.v1", "sys": args.system,
                          "max_tokens": args.max_tokens}, sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


def _stable_json(x):
    return json.dumps(x, sort_keys=True, default=str, ensure_ascii=False)


def _phash(prompt):
    return hashlib.sha1(prompt.encode()).hexdigest()[:12]


def _row_hash(*parts):
    return hashlib.sha1("\0".join(str(p) for p in parts).encode()).hexdigest()[:16]


def generate(task, n, workers=1):
    """Generate n FRESH (non-deterministic — no seeding) examples; return (examples, mean_gen_s).
    workers>1 = real ProcessPoolExecutor procs (~2x on pure-Python tasks); prover tasks
    (rocq/lean/tptp) can't run in the pool, so fall back to serial for those."""
    try:
        exs = task.generate_balanced_batch(batch_size=n, workers=workers)[:n]
    except BrokenProcessPool:
        exs = task.generate_balanced_batch(batch_size=n, workers=1)[:n]
    times = [e.metadata.get("_time") for e in exs if e.metadata.get("_time") is not None]
    return exs, (sum(times) / len(times) if times else None)


def load_preds(path):
    """Return dict keyed (task, model, sig, row_hash-or-phash) -> row."""
    rows = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            rows[(r["task"], r["model"], r["sig"], r.get("row_hash") or r["phash"])] = r
    return rows


def save_preds(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows.values(), key=lambda r: (r["task"], r["model"], r.get("row_hash") or r["phash"]))
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in ordered))


# ── PILE + by-LEVEL mode (rc vs rg across difficulty levels) ────────────────────────────────
# Sources held-out examples from the HF piles (which carry {task,prompt,answer,metadata,level})
# instead of the in-repo generators, so it covers BOTH rc and rg and stratifies by `level`. Scores
# with the unified reasoning_core.score_answer (rc + rg-wrapper via metadata). Same litlm plumbing,
# slow/serial/backoff, resume-safe. Needs reasoning_gym importable for rg (conda libstdc++ + Agg).
PILE_REPO = {"rc": "reasoning-core/procedural-pretraining-pile",
             "rg": "reasoning-core/reasoning-gym"}
_RG_FN = {}


def pile_pool(ds, n_per_level, scan_cap, cache_dir, refresh=False):
    """First-n-per-(task,level) FULL rows streamed from the HF pile; cached for stable restarts."""
    from datasets import load_dataset
    pf = cache_dir / f"zs_pool_{ds}.jsonl"
    if pf.exists() and not refresh:
        return [_stamp_pile_row(json.loads(l)) for l in pf.open()]
    counts, rows, scanned = {}, [], 0
    for x in load_dataset(PILE_REPO[ds], split="train", streaming=True):
        scanned += 1
        t = (x.get("task") or "").strip(); lv = x.get("level")
        if not t or t == "reasoning_gym" or lv is None or not x.get("answer") or not x.get("prompt"):
            continue
        k = (t, str(lv))
        if counts.get(k, 0) < n_per_level:
            rows.append(_stamp_pile_row({
                "src": ds, "task": t, "level": str(lv), "idx": counts.get(k, 0),
                "prompt": x["prompt"], "answer": x["answer"], "metadata": x.get("metadata"),
            }))
            counts[k] = counts.get(k, 0) + 1
        if scanned >= scan_cap:
            break
    pf.parent.mkdir(parents=True, exist_ok=True)
    with pf.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"[pile] {ds}: {len(counts)} (task,level) buckets, {len(rows)} ex (scanned {scanned})", flush=True)
    return rows


def _stamp_pile_row(row):
    md = row.get("metadata")
    md = md if isinstance(md, str) else _stable_json(md or {})
    row["metadata"] = md
    row["row_hash"] = row.get("row_hash") or _row_hash(
        row.get("src", ""), row.get("task", ""), row.get("level", ""),
        row.get("prompt", ""), row.get("answer", ""), md,
    )
    return row


def _row_dict(row):
    return row.to_dict() if hasattr(row, "to_dict") else dict(row)


def _row_series(row):
    if hasattr(row, "to_series"):
        return row.to_series()
    import pandas as pd
    return pd.Series(row)


def score_native(row, pred):
    """Native reward via reasoning_core.score_answer (needs a pandas Series for attr access); falls
    back to reasoning_gym's scorer for checkouts whose rg routing is skewed. Float, or None on error."""
    import reasoning_core
    d = _row_dict(row)
    try:
        return float(reasoning_core.score_answer(pred, _row_series(row)))
    except Exception:
        try:
            import pandas as pd
            import reasoning_gym
            md = d.get("metadata")
            md = json.loads(md) if isinstance(md, str) else (md or {})
            fn = _RG_FN.get(d["task"]) or reasoning_gym.get_score_answer_fn(d["task"])
            _RG_FN[d["task"]] = fn
            return float(fn(pred, pd.Series({"question": d["prompt"], "answer": d["answer"],
                                             "metadata": md})))
        except Exception:
            return None


def pile_report(preds_path, active_hashes=None):
    """Mean native reward by source × level (higher = easier), + hardest tasks. Safe mid-run."""
    from collections import defaultdict
    rows = []
    if preds_path.exists():
        for l in preds_path.open():
            r = json.loads(l)
            if active_hashes is not None and r.get("row_hash") not in active_hashes:
                continue
            if r.get("score") is not None:
                rows.append(r)
    if not rows:
        print("[pile] no scored rows yet"); return
    by_sl, by_st = defaultdict(list), defaultdict(list)
    models = sorted({r["model"] for r in rows})
    for r in rows:
        by_sl[(r["src"], str(r["level"]))].append(r["score"])
        by_st[(r["src"], r["task"])].append(r["score"])
    levels = sorted({lv for _, lv in by_sl})
    print(f"\n# zero-shot hardness rc vs rg (native score_answer) — {len(rows)} scored, models={models}")
    for src in ("rc", "rg"):
        cells = [f"L{lv}:{sum(by_sl[(src,lv)])/len(by_sl[(src,lv)]):.2f}(n={len(by_sl[(src,lv)])})"
                 for lv in levels if (src, lv) in by_sl]
        allv = [x for (s, _), v in by_sl.items() if s == src for x in v]
        print(f"  {src}:  " + "  ".join(cells) + (f"   | all={sum(allv)/len(allv):.2f}" if allv else ""))


def run_pile_levels(args):
    import litlm, time as _time, random as _random
    preds = Path(args.preds); preds.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if preds.exists():
        for l in preds.open():
            try:
                r = json.loads(l); done.add((r["src"], r["task"], r["level"], r["model"], r.get("row_hash")))
            except Exception:
                pass
    work = []
    active_hashes = set()
    for ds in args.datasets:
        for r in pile_pool(ds, args.n, args.scan_cap, preds.parent, refresh=args.refresh):
            active_hashes.add(r["row_hash"])
            for m in args.models:
                if (ds, r["task"], r["level"], m, r["row_hash"]) not in done:
                    work.append((m, r))
    work.sort(key=lambda w: (w[1]["idx"], w[0], w[1]["src"], w[1]["task"], w[1]["level"]))
    print(f"[pile] {len(work)} (model,example) to score  models={args.models}  done={len(done)}", flush=True)
    out = preds.open("a")
    t0 = _time.time(); delay = args.sleep; n429 = 0
    for i, (model, r) in enumerate(work):
        for attempt in range(8):
            try:
                res = litlm.complete([r["prompt"]], model=model, system=args.system, caching=True,
                                     max_tokens=args.max_tokens, show_progress=False,
                                     num_retries=args.num_retries, max_concurrency=args.max_concurrency)
                pred = litlm.extract_answer(res[0] or "") or ""
                out.write(json.dumps({"src": r["src"], "task": r["task"], "level": r["level"],
                    "model": model, "idx": r["idx"], "row_hash": r["row_hash"],
                    "gold": str(r["answer"])[:400],
                    "pred": str(pred)[:400], "score": score_native(r, pred), "ts": _time.time()}) + "\n")
                out.flush()
                if args.adaptive:                        # AIMD: gently relax the base rate on success
                    delay = max(args.sleep, delay * 0.97)
                break
            except Exception as e:
                rate = "429" in str(e) or "ratelimit" in (type(e).__name__ + str(e)).lower()
                n429 += rate
                if rate and args.adaptive:               # AIMD: multiplicatively back off the base rate
                    delay = min(delay * 1.5, args.max_delay)
                w = min((delay if rate else 1.0) * (1.6 ** attempt) + _random.random(), 120)
                print(f"[retry{attempt}] {r['src']}/{r['task']}/L{r['level']} "
                      f"{'429' if rate else type(e).__name__ + ':' + str(e)[:50]} sleep {w:.0f}s", flush=True)
                _time.sleep(w)
        if i % args.log_every == 0:                      # ETA logging (honest wall-clock incl. backoff)
            el = _time.time() - t0; rt = (i + 1) / el if el > 0 else 0
            eta = (len(work) - i - 1) / rt if rt > 0 else 0
            print(f"[prog] {i+1}/{len(work)} ({100*(i+1)/max(len(work),1):.1f}%)  rate={rt*60:.0f}/min  "
                  f"delay={delay:.1f}s  429s={n429}  elapsed={el/3600:.2f}h  ETA={eta/3600:.1f}h", flush=True)
        _time.sleep(delay)
    out.close()
    pile_report(preds, active_hashes)


def _load_cached_task_rows(args):
    try:
        from .cache import load_task_rows
    except ImportError:
        from cache import load_task_rows
    src = {"path": args.cache} if args.cache else {"repo": args.cache_repo, "revision": args.cache_revision}
    return list(load_task_rows(**src, tasks=args.tasks, levels=args.levels, n_per_task=args.n))


def run_taskrow_cache(args, rows, pred_rows):
    by_task = defaultdict(list)
    for row in rows:
        by_task[row.task].append(row)
    sig = _row_sig(args)
    active = set()
    for task_name in sorted(by_task):
        target = by_task[task_name][:args.n]
        wanted = {r.row_hash for r in target}
        for model in args.models:
            active.add((task_name, model, sig))
            if args.refresh:
                for k in [k for k in pred_rows if k[:3] == (task_name, model, sig) and k[3] in wanted]:
                    del pred_rows[k]
            have = sum(1 for r in target
                       if pred_rows.get((task_name, model, sig, r.row_hash), {}).get("ok"))
            todo = [r for r in target
                    if not pred_rows.get((task_name, model, sig, r.row_hash), {}).get("ok")]
            if not todo:
                print(f"{task_name:<30} {model:<42} cached ({have}/{len(target)})", flush=True)
                continue
            if args.dry_run:
                continue
            try:
                outs = litlm.complete([r.prompt for r in todo], model=model, system=args.system,
                                      caching=True, max_tokens=args.max_tokens, show_progress=False,
                                      max_concurrency=args.max_concurrency)
            except Exception as exc:
                print(f"{task_name:<30} {model:<42} API-ERR {type(exc).__name__}"[:110], flush=True)
                continue
            for r, o in zip(todo, outs):
                out = str(o)
                ans = litlm.extract_answer(out)
                pred_rows[(task_name, model, sig, r.row_hash)] = {
                    "task": task_name, "model": model, "sig": sig, "row_hash": r.row_hash,
                    "behavior_hash": r.behavior_hash, "task_version": r.task_version,
                    "level": r.level, "mode": r.mode, "phash": _phash(r.prompt),
                    "prompt": r.prompt, "gold": str(r.answer), "output": out, "answer": ans,
                    "score": score_native(r, ans), "ok": bool(out.strip()),
                }
            save_preds(Path(args.preds), pred_rows)
            okr = [pred_rows[(task_name, model, sig, r.row_hash)] for r in target
                   if pred_rows.get((task_name, model, sig, r.row_hash), {}).get("ok")]
            scored = [r["score"] for r in okr if r.get("score") is not None]
            mean = sum(scored) / len(scored) if scored else None
            tag = f"{mean:.3f}" if mean is not None else "n/a"
            print(f"{task_name:<30} {model:<42} reward={tag}  ({len(okr)}/{len(target)} ok)",
                  flush=True)
    return active


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", default=None, help="Tasks to eval (default: all registered).")
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS, help="litlm model ids (cheap/free).")
    ap.add_argument("--n", type=int, default=25, help="Target ok examples per (task, model); runs accumulate to it.")
    ap.add_argument("--max-tokens", type=int, default=640)
    ap.add_argument("--max-concurrency", type=int, default=8,
                    help="Cap simultaneous API calls (litlm semaphore) — lower for rate-limited free tiers.")
    ap.add_argument("--gen-workers", type=int, default=1,
                    help="Parallel generator processes (real ProcessPoolExecutor) — ~2x on pure-Python "
                         "generators; prover tasks (rocq/lean/tptp) auto-fall-back to serial.")
    ap.add_argument("--system", default=SYSTEM)
    ap.add_argument("--refresh", action="store_true", help="Recompute even where cached rows exist.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Report the cached aggregate to stdout — no generation, no API, no file writes.")
    ap.add_argument("--preds", default=str(ROOT / "task_diagnostics" / "zero_shot_preds.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "task_diagnostics" / "TASK_ZEROSHOT_RESULTS.json"))
    ap.add_argument("--cache", default=None, help="Evaluate rows from a local TaskRow Parquet cache.")
    ap.add_argument("--cache-repo", default=None, help="Evaluate rows from a HF dataset repo with TaskRow schema.")
    ap.add_argument("--cache-revision", default=None, help="Pinned HF revision for --cache-repo.")
    ap.add_argument("--levels", nargs="+", type=int, default=None, help="Filter cached rows by level.")
    # PILE + by-LEVEL mode (rc vs rg across levels) — omit for default in-repo generation mode.
    ap.add_argument("--datasets", nargs="+", default=None, choices=["rc", "rg"],
                    help="Pile/by-level hardness: stream these HF piles, stratify by `level`, score via "
                         "reasoning_core.score_answer. `--n` becomes examples per (task, level, model). "
                         "Writes to --preds (default zero_shot_levels_preds.jsonl in this mode).")
    ap.add_argument("--scan-cap", type=int, default=400000, help="[pile] max rows streamed per dataset.")
    ap.add_argument("--sleep", type=float, default=0.4, help="[pile] base inter-call delay (adaptive floor).")
    ap.add_argument("--adaptive", dest="adaptive", action="store_true", default=True,
                    help="[pile] AIMD adaptive delay: ×1.5 on 429, ×0.97 on success — auto-tunes to the "
                         "server's rate limit (on by default).")
    ap.add_argument("--no-adaptive", dest="adaptive", action="store_false",
                    help="[pile] fixed --sleep delay instead of AIMD.")
    ap.add_argument("--max-delay", type=float, default=15.0, help="[pile] adaptive delay ceiling (s).")
    ap.add_argument("--num-retries", type=int, default=3, help="[pile] litlm per-call retries (in-call backoff).")
    ap.add_argument("--log-every", type=int, default=25, help="[pile] progress+ETA log cadence (examples).")
    ap.add_argument("--report", action="store_true", help="[pile] print by-level report from --preds and exit.")
    args = ap.parse_args()

    if args.datasets:                                    # pile/by-level hardness mode
        if args.preds == str(ROOT / "task_diagnostics" / "zero_shot_preds.jsonl"):
            args.preds = str(ROOT / "task_diagnostics" / "zero_shot_levels_preds.jsonl")
        if args.report:
            pred_path = Path(args.preds)
            active = {
                r["row_hash"]
                for ds in args.datasets
                for r in pile_pool(ds, args.n, args.scan_cap, pred_path.parent, refresh=args.refresh)
            }
            return pile_report(pred_path, active)
        return run_pile_levels(args)

    preds_path, out_path = Path(args.preds), Path(args.out)
    rows = load_preds(preds_path)
    gen_time = {}
    active = set()

    if args.cache or args.cache_repo:
        cache_rows = _load_cached_task_rows(args)
        active = run_taskrow_cache(args, cache_rows, rows)
        md = _write_aggregate(out_path, rows, args, gen_time, active=active, write=not args.dry_run)
        if args.dry_run:
            print(md + f"\n[dry-run] would write {out_path} and {out_path.with_suffix('.md')}")
        else:
            print(f"\nwrote {preds_path}\nwrote {out_path}\nwrote {out_path.with_suffix('.md')}")
        return

    for name in (() if args.dry_run else (args.tasks or list_tasks())):  # dry-run: report cache only
        task = get_task(name)
        bh = task.behavior_hash()
        sig = _sig(bh, args)
        for model in args.models:
            active.add((name, model, sig))
            if args.refresh:                             # drop this (task, model, config) and recompute
                for k in [k for k in rows if k[:3] == (name, model, sig)]:
                    del rows[k]
            have = sum(1 for k in rows if k[:3] == (name, model, sig) and rows[k].get("ok"))
            need = max(0, args.n - have)                 # top up to n fresh, diverse examples
            if need == 0:
                print(f"{name:<30} {model:<42} cached ({have}/{args.n})", flush=True)
                continue
            try:
                exs, gt = generate(task, need, workers=args.gen_workers)
                gen_time[name] = gt
            except BaseException as exc:                 # framework TimeoutException is BaseException
                print(f"{name:<30} {model:<42} GEN-ERR {type(exc).__name__}"[:110], flush=True)
                continue
            try:
                outs = litlm.complete([e.prompt for e in exs], model=model, system=args.system,
                                      caching=True, max_tokens=args.max_tokens, show_progress=False,
                                      max_concurrency=args.max_concurrency)
            except Exception as exc:
                print(f"{name:<30} {model:<42} API-ERR {type(exc).__name__}"[:110], flush=True)
                continue
            for e, o in zip(exs, outs):
                out = str(o)
                ans = litlm.extract_answer(out)
                try:
                    score = float(task.score_answer(ans, e))
                except Exception:
                    score = 0.0
                rows[(name, model, sig, _phash(e.prompt))] = {
                    "task": name, "model": model, "sig": sig, "behavior_hash": bh,
                    "phash": _phash(e.prompt), "prompt": e.prompt, "gold": str(e.answer),
                    "output": out, "answer": ans, "score": score, "ok": bool(out.strip()),
                }
            save_preds(preds_path, rows)
            okr = [rows[k] for k in rows if k[:3] == (name, model, sig) and rows[k].get("ok")]
            mean = sum(r["score"] for r in okr) / len(okr) if okr else None
            tag = f"{mean:.3f}" if mean is not None else "n/a"
            print(f"{name:<30} {model:<42} reward={tag}  ({len(okr)}/{args.n} ok)", flush=True)

    if args.dry_run:
        for name in (args.tasks or list_tasks()):
            try:
                task = get_task(name)
                sig = _sig(task.behavior_hash(), args)
            except Exception:
                continue
            for model in args.models:
                active.add((name, model, sig))

    md = _write_aggregate(out_path, rows, args, gen_time, active=active, write=not args.dry_run)
    if args.dry_run:
        print(md + f"\n[dry-run] would write {out_path} and {out_path.with_suffix('.md')}")
    else:
        print(f"\nwrote {preds_path}\nwrote {out_path}\nwrote {out_path.with_suffix('.md')}")


def _write_aggregate(out_path, rows, args, gen_time, active=None, write=True):
    """Derive per-(task, model) reward from the per-example rows -> JSON + a small MD table.
    Returns the rendered MD; write=False (dry-run) skips both file writes."""
    prev = (json.loads(out_path.read_text()).get("tasks", {}) if out_path.exists() else {})
    by = defaultdict(list)
    for r in rows.values():
        if active is not None and (r["task"], r["model"], r["sig"]) not in active:
            continue
        by[r["task"]].append(r)
    tasks = {}
    for t, rs in by.items():
        models = {}
        for m in {r["model"] for r in rs}:
            okr = [r for r in rs if r["model"] == m and r.get("ok")]
            scored = [r["score"] for r in okr if r.get("score") is not None]
            models[m] = {"reward": (sum(scored) / len(scored)) if scored else None,
                         "n_ok": len(okr), "n": sum(r["model"] == m for r in rs)}
        gt = gen_time.get(t)                             # fall back to prior JSON on cached-only rebuilds
        tasks[t] = {"gen_time": gt if gt is not None else prev.get(t, {}).get("gen_time"),
                    "models": models}
    if write:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "n_per_task": args.n, "models": args.models, "system": args.system,
            "tasks": tasks,
        }, indent=2, sort_keys=True) + "\n")

    ms = sorted({m for t in tasks.values() for m in t["models"]})
    def rew(t, m): return (tasks[t]["models"].get(m) or {}).get("reward")
    def meanrew(t):
        vs = [rew(t, m) for m in ms if rew(t, m) is not None]
        return sum(vs) / len(vs) if vs else -1
    md = ["# Zero-shot task solvability", "",
          "Real free-gen reward (`task.score_answer`) via litlm — hardest first. Low reward on a "
          "capable model = genuinely hard/unlearnable (teacher-forced token_acc inflates). "
          "`gen` = mean generator s/example. Per-example labels: zero_shot_preds.jsonl (local).", "",
          "| task | " + " | ".join(m.split("/")[-1] + " ↑" for m in ms) + " | gen |",
          "|" + "---|" * (len(ms) + 2)]
    for t in sorted(tasks, key=meanrew):
        cells = [f"{rew(t, m):.2f}" if rew(t, m) is not None else "—" for m in ms]
        gt = tasks[t].get("gen_time")
        md.append(f"| {t} | " + " | ".join(cells) + (f" | {gt:.2f}s |" if gt is not None else " | — |"))
    text = "\n".join(md) + "\n"
    if write:
        out_path.with_suffix(".md").write_text(text)
    return text


if __name__ == "__main__":
    main()
