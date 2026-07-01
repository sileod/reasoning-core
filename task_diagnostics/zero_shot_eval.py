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

Hash-cached + incremental: each row is keyed by a signature over the task's
behavior_hash + n + system + max_tokens + seed. Re-runs recompute ONLY missing or
failed (ok=False) examples — so free-tier rate-limit gaps self-heal on re-run, and
unchanged work is skipped. Pass --refresh to force recompute.

  python task_diagnostics/zero_shot_eval.py
  python task_diagnostics/zero_shot_eval.py --tasks logic_nli count_elements analogical_case_retrieval
  python task_diagnostics/zero_shot_eval.py --models nvidia_nim/nvidia/nemotron-3-super-120b-a12b --n 25
"""
import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reasoning_core import get_task, list_tasks  # noqa: E402
import litlm  # noqa: E402

DEFAULT_MODELS = [                                       # free NVIDIA NIM endpoints (need NVIDIA_NIM_API_KEY)
    "nvidia_nim/meta/llama-3.1-8b-instruct",             # small, fast, reliable instruct
    "nvidia_nim/meta/llama-3.3-70b-instruct",            # stronger instruct reference
]                                                         # plain instruct > reasoning models here (clean answers, no <think>)
SYSTEM = (
    "You are solving a reasoning task. Read the problem and reply with ONLY the final "
    "answer, in exactly the format the problem asks for — no explanation. Put the final "
    "answer inside <answer></answer> tags."
)


def _sig(behavior_hash, args):
    """Signature that invalidates cached predictions when the task or eval config changes."""
    payload = json.dumps({"bh": behavior_hash, "n": args.n, "sys": args.system,
                          "max_tokens": args.max_tokens, "seed": args.seed}, sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


def _phash(prompt):
    return hashlib.sha1(prompt.encode()).hexdigest()[:12]


def generate(task, n, seed):
    """Generate n examples once per task; return (examples, mean_gen_seconds)."""
    random.seed(seed)
    exs = task.generate_balanced_batch(batch_size=n)[:n]
    times = [e.metadata.get("_time") for e in exs if e.metadata.get("_time") is not None]
    return exs, (sum(times) / len(times) if times else None)


def load_preds(path):
    """Return dict keyed (task, model, sig, phash) -> row."""
    rows = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            rows[(r["task"], r["model"], r["sig"], r["phash"])] = r
    return rows


def save_preds(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows.values(), key=lambda r: (r["task"], r["model"], r["phash"]))
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in ordered))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", default=None, help="Tasks to eval (default: all registered).")
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS, help="litlm model ids (cheap/free).")
    ap.add_argument("--n", type=int, default=25, help="Examples per task (default 25).")
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--max-tokens", type=int, default=640)
    ap.add_argument("--system", default=SYSTEM)
    ap.add_argument("--refresh", action="store_true", help="Recompute even where cached rows exist.")
    ap.add_argument("--preds", default=str(ROOT / "task_diagnostics" / "zero_shot_preds.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "task_diagnostics" / "ZERO_SHOT.json"))
    args = ap.parse_args()

    preds_path, out_path = Path(args.preds), Path(args.out)
    rows = load_preds(preds_path)
    gen_time = {}

    for name in (args.tasks or list_tasks()):
        task = get_task(name)
        bh = task.behavior_hash()
        sig = _sig(bh, args)
        exs = None                                       # lazy: only generate if some model needs work
        for model in args.models:
            done = {k[3] for k in rows if k[0] == name and k[1] == model and k[2] == sig
                    and rows[k].get("ok")}
            if exs is None:
                try:
                    exs, gt = generate(task, args.n, args.seed)
                    gen_time[name] = gt
                except BaseException as exc:             # framework TimeoutException is BaseException
                    print(f"{name:<30} GEN-ERR {type(exc).__name__}: {exc}"[:110], flush=True)
                    exs = []
            todo = [e for e in exs if args.refresh or _phash(e.prompt) not in done]
            if not todo:
                print(f"{name:<30} {model:<42} cached ({len(done)}/{args.n})", flush=True)
                continue
            try:
                outs = litlm.complete([e.prompt for e in todo], model=model, system=args.system,
                                      caching=True, max_tokens=args.max_tokens, show_progress=False)
            except Exception as exc:
                print(f"{name:<30} {model:<42} API-ERR {type(exc).__name__}"[:110], flush=True)
                continue
            for e, o in zip(todo, outs):
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
            ok = [rows[(name, model, sig, _phash(e.prompt))] for e in exs
                  if (name, model, sig, _phash(e.prompt)) in rows]
            okr = [r for r in ok if r["ok"]]
            mean = sum(r["score"] for r in okr) / len(okr) if okr else None
            tag = f"{mean:.3f}" if mean is not None else "n/a"
            print(f"{name:<30} {model:<42} reward={tag}  ({len(okr)}/{args.n} ok)", flush=True)

    _write_aggregate(out_path, rows, args, gen_time)
    print(f"\nwrote {preds_path}\nwrote {out_path}")


def _write_aggregate(out_path, rows, args, gen_time):
    """Derive per-(task, model) reward from the per-example rows. Report-card rendering
    (combined with influence/saturation) lives in the diagnostics aggregator, not here."""
    by = defaultdict(list)
    for r in rows.values():
        by[r["task"]].append(r)
    tasks = {}
    for t, rs in by.items():
        models = {}
        for m in {r["model"] for r in rs}:
            okr = [r for r in rs if r["model"] == m and r.get("ok")]
            models[m] = {"reward": (sum(r["score"] for r in okr) / len(okr)) if okr else None,
                         "n_ok": len(okr), "n": sum(r["model"] == m for r in rs)}
        tasks[t] = {"gen_time": gen_time.get(t), "models": models}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_per_task": args.n, "models": args.models, "system": args.system,
        "tasks": tasks,
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
