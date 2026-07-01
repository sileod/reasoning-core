#!/usr/bin/env python
"""Zero-shot task-solvability eval via litlm + OpenRouter (cheap models, ~25 ex/task).

Measures REAL free-generation reward (task.score_answer) — the honest counterpart to
teacher-forced token accuracy, which inflates on tasks a model can "follow" but not
"lead". A low zero-shot reward on a capable model means the task is genuinely hard
(or unlearnable); a high one means it is easy/solvable.

Reproducible on ANY machine: uses the in-repo task generators + litlm. No data_cache,
no local GPU, no training. Requires `pip install litlm` and a provider key in the env:
  NVIDIA_NIM_API_KEY  (default models — free NVIDIA NIM endpoints), or
  OPENROUTER_API_KEY  (for --models openrouter/...).

  python task_diagnostics/zero_shot_eval.py                         # all tasks, default free NIM models
  python task_diagnostics/zero_shot_eval.py --tasks logic_nli count_elements analogical_case_retrieval
  python task_diagnostics/zero_shot_eval.py --models nvidia_nim/nvidia/nemotron-3-super-120b-a12b --n 25
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reasoning_core import get_task, list_tasks  # noqa: E402
import litlm  # noqa: E402

DEFAULT_MODELS = [                                       # free NVIDIA NIM endpoints (need NVIDIA_NIM_API_KEY)
    "nvidia_nim/meta/llama-3.1-8b-instruct",             # small, fast, clean instruct
    "nvidia_nim/nvidia/nvidia-nemotron-nano-9b-v2",      # small Nemotron
]                                                         # add a strong ref (e.g. nvidia_nim/nvidia/nemotron-3-super-120b-a12b) or openrouter/... via --models
SYSTEM = (
    "You are solving a reasoning task. Read the problem and reply with ONLY the final "
    "answer, in exactly the format the problem asks for — no explanation. Put the final "
    "answer inside <answer></answer> tags."
)


def eval_task(name, model, n, seed, max_tokens, system):
    """Return (mean_reward, n_scored, error_or_None) for one task under one model."""
    task = get_task(name)
    try:
        exs = task.generate_balanced_batch(batch_size=n)
    except BaseException as exc:  # framework TimeoutException is BaseException
        return None, 0, f"gen failed: {type(exc).__name__}: {exc}"
    exs = exs[:n]
    if not exs:
        return None, 0, "no examples"
    prompts = [e.prompt for e in exs]
    try:
        outs = litlm.complete(prompts, model=model, system=system,
                              caching=True, max_tokens=max_tokens, show_progress=False)
    except Exception as exc:
        return None, 0, f"api failed: {type(exc).__name__}: {exc}"
    rewards = []
    for e, o in zip(exs, outs):
        ans = litlm.extract_answer(str(o))          # inner <answer> or the raw text
        try:
            rewards.append(float(task.score_answer(ans, e)))
        except Exception:
            rewards.append(0.0)
    return (sum(rewards) / len(rewards), len(rewards), None) if rewards else (None, 0, "no scores")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", default=None, help="Tasks to eval (default: all registered).")
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS, help="litlm/OpenRouter model ids (cheap).")
    ap.add_argument("--n", type=int, default=25, help="Examples per task (default 25).")
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--system", default=SYSTEM)
    ap.add_argument("--out", default=str(ROOT / "task_diagnostics" / "ZERO_SHOT.json"))
    args = ap.parse_args()

    tasks = args.tasks or list_tasks()
    out_path = Path(args.out)
    results = {}
    if out_path.exists():
        try:
            results = json.loads(out_path.read_text()).get("tasks", {})
        except Exception:
            results = {}

    for name in tasks:
        results.setdefault(name, {})
        for model in args.models:
            mean, k, err = eval_task(name, model, args.n, args.seed, args.max_tokens, args.system)
            results[name][model] = {"reward": mean, "n": k, "error": err}
            tag = f"{mean:.3f}" if mean is not None else f"ERR({err})"
            print(f"{name:<32} {model:<40} reward={tag}  (n={k})", flush=True)
        # persist after each task so a mid-run stop keeps progress
        _write(out_path, results, args)

    _write_markdown(out_path.with_suffix(".md"), results, args)
    print(f"\nwrote {out_path}\nwrote {out_path.with_suffix('.md')}")


def _write(out_path, results, args):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_per_task": args.n, "models": args.models, "system": args.system,
        "tasks": results,
    }, indent=2, sort_keys=True) + "\n")


def _write_markdown(path, results, args):
    models = args.models
    lines = ["# Zero-shot task solvability", "",
             f"Real free-gen reward (task.score_answer), {args.n} examples/task, via litlm+OpenRouter.",
             "Low reward on a capable model = genuinely hard/unlearnable (vs teacher-forced token_acc, which inflates).",
             ""]
    header = "| task | " + " | ".join(m.split("/")[-1] for m in models) + " |"
    lines += [header, "|" + "---|" * (len(models) + 1)]
    def keyfn(t):
        vals = [results[t].get(m, {}).get("reward") for m in models]
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else -1
    for t in sorted(results, key=keyfn):
        cells = []
        for m in models:
            r = results[t].get(m, {}).get("reward")
            cells.append(f"{r:.2f}" if r is not None else "—")
        lines.append(f"| {t} | " + " | ".join(cells) + " |")
    path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
