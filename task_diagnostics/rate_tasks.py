#!/usr/bin/env python
"""LLM-as-judge DATA-QUALITY rating (eval CONSTRUCTION) — a cheap predictor of task usefulness.

Idea (user): show a model a BATCH of examples from a task and ask it to SCORE the dataset on holistic
axes ("how interesting/diverse/deep the data feels", "would training on this help a small reasoner").
Those subjective 1-10 ratings are instant + cheap (one call per task) and may correlate with the slow
per-task GPU influence — a heuristic to pre-screen tasks. Analysis/correlation lives elsewhere
(cheap_predictors.py); this file only PRODUCES the ratings.

Cost is tiny (~1 call/task). Same litlm plumbing + the free NVIDIA-NIM or paid OpenRouter provider.
Ratings are hash-cached by (task, model, behavior_hash, rubric) and appended to task_ratings.jsonl.

  python task_diagnostics/rate_tasks.py --model openrouter/meta-llama/llama-3.3-70b-instruct --k 8
  python task_diagnostics/rate_tasks.py --tasks defeasible_nli code_analysis --k 8
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from reasoning_core import get_task, list_tasks  # noqa: E402
import litlm  # noqa: E402

AXES = ["interestingness", "diversity", "reasoning_depth", "difficulty",
        "learnability", "training_usefulness"]
RUBRIC = (
    "You are a data curator assessing a PROCEDURAL TRAINING dataset used to teach a SMALL language "
    "model to reason. Below is a random batch of examples from ONE task (each = a problem and its "
    "correct answer). Judge the TASK as training data on a 1-10 scale (10 = best) on these axes:\n"
    "- interestingness: does the data feel rich/interesting vs trivial or repetitive?\n"
    "- diversity: how varied are the problems (structure, content)?\n"
    "- reasoning_depth: how many genuine reasoning steps are required?\n"
    "- difficulty: how hard are the problems?\n"
    "- learnability: could a small model plausibly LEARN the pattern from such examples?\n"
    "- training_usefulness: how much would training on this task improve GENERAL reasoning?\n"
    "Reply with ONLY a compact JSON object mapping each axis to an integer 1-10, e.g. "
    '{"interestingness":7,"diversity":6,"reasoning_depth":8,"difficulty":7,"learnability":5,'
    '"training_usefulness":6}. No prose.'
)


def _sig(behavior_hash, k, rubric):
    payload = json.dumps({"bh": behavior_hash, "k": k,
                          "rubric": hashlib.sha1(rubric.encode()).hexdigest()[:8]}, sort_keys=True)
    return hashlib.sha1(payload.encode()).hexdigest()[:16]


def load(path):
    rows = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                rows[(r["task"], r["model"], r["sig"])] = r
    return rows


def save(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n"
                            for r in sorted(rows.values(), key=lambda r: (r["task"], r["model"]))))


def parse_scores(text):
    """Pull the JSON object of axis->int from the model reply (tolerant of prose/code fences)."""
    m = re.search(r"\{[^{}]*\}", text or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except Exception:
        return None
    out = {}
    for a in AXES:
        v = d.get(a)
        try:
            out[a] = max(1, min(10, int(round(float(v)))))
        except Exception:
            out[a] = None
    return out if any(v is not None for v in out.values()) else None


def batch_block(task, k):
    """K fresh examples rendered compactly (long prompts/answers truncated to keep the call cheap)."""
    try:
        task.base_timeout = task.timeout = 6           # bound per-example gen so no task stalls the run
    except Exception:
        pass
    exs = task.generate_balanced_batch(batch_size=k, workers=1)[:k]
    lines = []
    for i, e in enumerate(exs, 1):
        p = " ".join(str(e.prompt).split())[:500]
        a = " ".join(str(e.answer).split())[:120]
        lines.append(f"[Example {i}]\nProblem: {p}\nAnswer: {a}")
    return "\n\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", default=None)
    ap.add_argument("--model", default="openrouter/meta-llama/llama-3.3-70b-instruct")
    ap.add_argument("--k", type=int, default=8, help="Examples shown per task in the rated batch.")
    ap.add_argument("--max-tokens", type=int, default=120)
    ap.add_argument("--max-concurrency", type=int, default=3)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "task_diagnostics" / "task_ratings.jsonl"))
    args = ap.parse_args()

    path = Path(args.out)
    rows = load(path)
    names = args.tasks or list_tasks()
    todo = []
    for name in names:
        try:
            task = get_task(name)
            bh = task.behavior_hash()
        except Exception as exc:
            print(f"{name:<30} SKIP {type(exc).__name__}", flush=True); continue
        sig = _sig(bh, args.k, RUBRIC)
        if not args.refresh and (name, args.model, sig) in rows and rows[(name, args.model, sig)].get("scores"):
            print(f"{name:<30} cached", flush=True); continue
        try:
            block = batch_block(task, args.k)
        except BaseException as exc:
            print(f"{name:<30} GEN-ERR {type(exc).__name__}", flush=True); continue
        todo.append((name, bh, sig, block))

    for name, bh, sig, block in todo:
        prompt = f"Task name: {name}\n\n{block}\n\nNow output the JSON ratings."
        try:
            out = str(litlm.complete([prompt], model=args.model, system=RUBRIC, caching=True,
                                     max_tokens=args.max_tokens, show_progress=False,
                                     max_concurrency=args.max_concurrency)[0])
        except Exception as exc:
            print(f"{name:<30} API-ERR {type(exc).__name__}", flush=True); continue
        scores = parse_scores(out)
        rows[(name, args.model, sig)] = {"task": name, "model": args.model, "sig": sig,
                                         "behavior_hash": bh, "k": args.k, "raw": out[:400],
                                         "scores": scores}
        save(path, rows)
        tag = "  ".join(f"{a[:4]}={scores[a]}" for a in AXES if scores and scores.get(a) is not None) if scores else "PARSE-FAIL"
        print(f"{name:<30} {tag}", flush=True)

    try:
        cb = litlm.cost_breakdown(period="day", by="model")
        if cb:
            print(f"[cost] this run ${sum(cb.values()):.4f}", flush=True)
    except Exception:
        pass
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
