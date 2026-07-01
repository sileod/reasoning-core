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
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
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


def _phash(prompt):
    return hashlib.sha1(prompt.encode()).hexdigest()[:12]


def generate(task, n):
    """Generate n FRESH (non-deterministic — no seeding) examples; return (examples, mean_gen_s)."""
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
    ap.add_argument("--n", type=int, default=25, help="Target ok examples per (task, model); runs accumulate to it.")
    ap.add_argument("--max-tokens", type=int, default=640)
    ap.add_argument("--max-concurrency", type=int, default=8,
                    help="Cap simultaneous API calls (litlm semaphore) — lower for rate-limited free tiers.")
    ap.add_argument("--system", default=SYSTEM)
    ap.add_argument("--refresh", action="store_true", help="Recompute even where cached rows exist.")
    ap.add_argument("--preds", default=str(ROOT / "task_diagnostics" / "RESULTS" / "zero_shot_preds.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "task_diagnostics" / "RESULTS" / "ZERO_SHOT.json"))
    args = ap.parse_args()

    preds_path, out_path = Path(args.preds), Path(args.out)
    rows = load_preds(preds_path)
    gen_time = {}

    for name in (args.tasks or list_tasks()):
        task = get_task(name)
        bh = task.behavior_hash()
        sig = _sig(bh, args)
        for model in args.models:
            if args.refresh:                             # drop this (task, model, config) and recompute
                for k in [k for k in rows if k[:3] == (name, model, sig)]:
                    del rows[k]
            have = sum(1 for k in rows if k[:3] == (name, model, sig) and rows[k].get("ok"))
            need = max(0, args.n - have)                 # top up to n fresh, diverse examples
            if need == 0:
                print(f"{name:<30} {model:<42} cached ({have}/{args.n})", flush=True)
                continue
            try:
                exs, gt = generate(task, need)
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

    _write_aggregate(out_path, rows, args, gen_time)
    print(f"\nwrote {preds_path}\nwrote {out_path}\nwrote {out_path.with_suffix('.md')}")


def _write_aggregate(out_path, rows, args, gen_time):
    """Derive per-(task, model) reward from the per-example rows -> JSON + a small MD table."""
    prev = (json.loads(out_path.read_text()).get("tasks", {}) if out_path.exists() else {})
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
        gt = gen_time.get(t)                             # fall back to prior JSON on cached-only rebuilds
        tasks[t] = {"gen_time": gt if gt is not None else prev.get(t, {}).get("gen_time"),
                    "models": models}
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
    out_path.with_suffix(".md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
