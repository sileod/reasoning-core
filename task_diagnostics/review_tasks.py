#!/usr/bin/env python
"""LLM CODE-REVIEW of reasoning tasks — a free, CPU-only task-health audit.

For each task we show a strong model (a) the generator SOURCE (via inspect) and (b) a balanced batch of
generated examples (prompt+answer only — metadata is bloat), and ask for a graded JSON review on the
design axes we care about: label soundness, shortcut-resistance, prompt/answer conciseness, answer
canonicity (+ free-form notes). Each axis gets an integer score (1-10) and a one-line comment.

Free via NVIDIA NIM (needs NVIDIA_NIM_API_KEY, auto-loaded from ~/.nvapi_key). The free tier hard-quotas,
so we WAIT aggressively (exponential backoff, never skip) and cache every result to jsonl — ~50 tasks
grind over the day and a restart resumes instantly.

  python task_diagnostics/review_tasks.py                              # all tasks, default models
  python task_diagnostics/review_tasks.py --tasks constraint_satisfaction string_transduction
  python task_diagnostics/review_tasks.py --models nvidia_nim/deepseek-ai/deepseek-v4-pro
  python task_diagnostics/review_tasks.py --report                     # print the sorted health report
"""
import argparse, hashlib, inspect, json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reasoning_core import get_task, list_tasks  # noqa: E402
import litlm  # noqa: E402

os.environ.setdefault("NVIDIA_NIM_API_KEY",
                      (Path.home() / ".nvapi_key").read_text().strip() if (Path.home() / ".nvapi_key").exists() else "")

# Strong + RESPONSIVE NIM reviewers (probed 2026-07-12): glm-5.2 (~40s) and deepseek-v4-flash (~1s).
# Avoid deepseek-v4-PRO (600s hangs, timeout not enforced) and qwen3-next-80b (>130s).
DEFAULT_MODELS = ["nvidia_nim/z-ai/glm-5.2",
                  "nvidia_nim/deepseek-ai/deepseek-v4-flash"]

AXES = {
    "label_soundness":     "Are the gold answers correct and unambiguous given the prompt? Penalize wrong, ill-defined, or multiple-valid-answer cases.",
    "shortcut_resistance": "Must the answer come from genuine reasoning, or can it be guessed from surface cues (answer length, a keyword, position, label frequency)? High = shortcut-resistant.",
    "prompt_conciseness":  "Is the prompt free of boilerplate/redundancy — short, clear instructions? Token budget matters.",
    "answer_conciseness":  "Is the answer minimal — few tokens, no verbose formatting or filler?",
    "answer_canonicity":   "Is there exactly ONE canonical surface form per answer (deterministic normalization) so exact-match scoring is fair? Penalize when many renderings are equally valid.",
}
SHORT = {"label_soundness": "label", "shortcut_resistance": "shcut", "prompt_conciseness": "p.conc",
         "answer_conciseness": "a.conc", "answer_canonicity": "a.canon"}
SYSTEM = (
    "You are a senior reviewer of PROCEDURAL TRAINING TASKS for small language models. You are given a "
    "task's generator SOURCE CODE and a batch of its generated (problem, answer) pairs. Review the task "
    "on each axis below, scoring 1-10 (10 = excellent) with a concise (<=25 word) justification:\n"
    + "".join(f"- {a}: {d}\n" for a, d in AXES.items()) +
    'Reply with ONLY a JSON object: {"<axis>": {"score": <int 1-10>, "comment": "<text>"}, ...} for every '
    'axis, plus "other": "<any other design issue you notice, or empty>". No prose outside the JSON.'
)


def task_source(task, cap=16000):
    cls = type(task)
    try:
        src = inspect.getsource(inspect.getmodule(cls))
    except Exception:
        src = inspect.getsource(cls)
    return src[:cap] + ("\n… (truncated)" if len(src) > cap else "")


def batch_block(task, k):
    try:
        task.base_timeout = task.timeout = 6           # bound per-example gen so no task stalls the run
    except Exception:
        pass
    exs = task.generate_balanced_batch(batch_size=k, workers=1)[:k]
    return "\n\n".join(
        f"[Example {i}]\nProblem: {' '.join(str(e.prompt).split())[:600]}\nAnswer: {' '.join(str(e.answer).split())[:160]}"
        for i, e in enumerate(exs, 1))


def sig(bh, k):
    return hashlib.sha1(f"{bh}|{k}|{hashlib.sha1(SYSTEM.encode()).hexdigest()[:8]}".encode()).hexdigest()[:16]


def _axis(v):
    """Accept either nested {'score':n,'comment':..} or a flat number — models vary in shape."""
    if isinstance(v, dict):
        s, c = v.get("score", v.get("rating")), v.get("comment", v.get("reason", ""))
    else:
        s, c = v, ""
    return {"score": max(1, min(10, int(round(float(s))))), "comment": str(c)[:200]}


def normalize(d):
    """Clamp scores to 1-10 and trim comments; litlm's json=True already parsed the model reply to a dict."""
    out = {}
    for a in AXES:
        try:
            out[a] = _axis(d[a]) if d.get(a) is not None else None
        except Exception:
            out[a] = None
    out["other"] = str(d.get("other", "") or "")[:300]
    return out if any(out[a] for a in AXES) else None


def review_one(prompt, model, max_tokens, tries=40):
    """One review dict from a model. litlm handles JSON parsing, disk cache and short retries; the outer
    loop just WAITS through the free-tier quota (long backoff) so the 50-task run grinds over the day."""
    delay = 20
    for attempt in range(tries):
        try:
            d = litlm.complete([prompt], model=model, system=SYSTEM, json=True, caching=True, num_retries=4,
                               max_tokens=max_tokens, timeout=180, show_progress=False, max_concurrency=1)[0]
            return normalize(d)
        except Exception as exc:
            w = min(delay, 600)
            print(f"    [wait] {type(exc).__name__}: {str(exc)[:60]} — sleep {w}s ({attempt+1}/{tries})", flush=True)
            time.sleep(w); delay = int(delay * 1.6)
    return None


def load(path):
    rows = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip():
                r = json.loads(line); rows[(r["task"], r["model"], r["sig"])] = r
    return rows


def save(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n"
                            for r in sorted(rows.values(), key=lambda r: (r["task"], r["model"]))))


def report(path):
    rows = [r for r in load(path).values() if r.get("review")]
    by = {}
    for r in rows:
        by.setdefault(r["task"], []).append(r["review"])
    def axis_mean(revs, a):
        vs = [rv[a]["score"] for rv in revs if rv.get(a)]
        return sum(vs) / len(vs) if vs else None
    table = []
    for t, revs in by.items():
        means = {a: axis_mean(revs, a) for a in AXES}
        vals = [v for v in means.values() if v is not None]
        table.append((t, sum(vals) / len(vals) if vals else 0, means, len(revs)))
    table.sort(key=lambda x: x[1])                      # worst overall first = needs attention
    W = max((len(t) for t, *_ in table), default=12)
    head = f"{'task':<{W}}  {'overall':>7}  " + "  ".join(f"{SHORT[a]:>7}" for a in AXES)
    lines = [f"# Task health review ({len(table)} tasks, {sum(r for *_, r in table)} reviews)  worst-first\n", head, "-" * len(head)]
    for t, ov, means, n in table:
        cells = "  ".join((f"{means[a]:>7.1f}" if means[a] is not None else f"{'.':>7}") for a in AXES)
        flag = "  ⚠" + ",".join(SHORT[a] for a in AXES if means[a] is not None and means[a] < 5) if any(means[a] is not None and means[a] < 5 for a in AXES) else ""
        lines.append(f"{t:<{W}}  {ov:>7.2f}  {cells}{flag}")
    out = "\n".join(lines)
    print(out)
    rp = path.with_suffix(".report.md"); rp.write_text(out + "\n")
    print(f"\nwrote {rp}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", default=None)
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--k", type=int, default=8, help="examples shown per task")
    ap.add_argument("--max-tokens", type=int, default=2200, help="room for reasoning models to finish + emit JSON")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--report", action="store_true", help="just print the sorted health report")
    ap.add_argument("--out", default=str(ROOT / "task_diagnostics" / "task_reviews.jsonl"))
    args = ap.parse_args()
    path = Path(args.out)

    if args.report:
        return report(path)

    rows = load(path)
    names = args.tasks or list_tasks()
    for name in names:
        try:
            task = get_task(name); bh = task.behavior_hash(); s = sig(bh, args.k)
        except Exception as exc:
            print(f"{name:<30} SKIP {type(exc).__name__}", flush=True); continue
        pending = [m for m in args.models if args.refresh or not (rows.get((name, m, s)) or {}).get("review")]
        if not pending:
            print(f"{name:<30} cached ({len(args.models)})", flush=True); continue
        try:
            code, block = task_source(task), batch_block(task, args.k)
        except BaseException as exc:
            print(f"{name:<30} GEN-ERR {type(exc).__name__}", flush=True); continue
        prompt = f"TASK: {name}\n\n=== GENERATOR SOURCE ===\n{code}\n\n=== GENERATED EXAMPLES ===\n{block}\n\nKeep any reasoning brief, then end your reply with ONLY the JSON review object."
        for m in pending:
            review = review_one(prompt, m, args.max_tokens)
            rows[(name, m, s)] = {"task": name, "model": m, "sig": s, "behavior_hash": bh,
                                  "k": args.k, "review": review}
            save(path, rows)
            if review:
                tag = " ".join(f"{SHORT[a]}={review[a]['score']}" for a in AXES if review.get(a))
                print(f"{name:<24} {m.split('/')[-1]:<20} {tag}", flush=True)
            else:
                print(f"{name:<24} {m.split('/')[-1]:<20} PARSE/API-FAIL", flush=True)
    print(f"\nwrote {path}  —  run with --report for the sorted health table")


if __name__ == "__main__":
    main()
