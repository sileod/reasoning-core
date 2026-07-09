#!/usr/bin/env python
"""ANALYSIS (read-only) of the few-shot ICL eval — kept SEPARATE from eval construction.

`zero_shot_eval.py --shots K` is the *construction* step: it calls the API and appends rows to
zero_shot_preds.jsonl (one per task/model/shots/example). This script does NO API calls; it reads
those predictions and derives:

  - per-task reward at each shot count (0 / 1 / 3 …) for one base model
  - the ICL lift = reward@K − reward@0  (an in-context-learnability signal:
    how much the FROZEN model picks the task up from a few worked examples)
  - correlation of that lift with other learnability signals:
      * zero-shot reward itself (headroom — does ICL help most where 0-shot is weak?)
      * train-time transfer value (per-task influence global%, if a ref run is given) —
        does "learnable in context" track "useful when trained on"?

Usage:
  python task_diagnostics/shots_lift_analysis.py                       # default preds + auto model
  python task_diagnostics/shots_lift_analysis.py --model nvidia_nim/meta/llama-3.1-8b-instruct
  python task_diagnostics/shots_lift_analysis.py --influence per_task_results/influence_LOCAL_bbf7208274_S43_T300_M20_fwdolci_pretrained.json
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREDS = ROOT / "task_diagnostics" / "zero_shot_preds.jsonl"


def load_rows(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def reward_by_shots(rows, model):
    """task -> {shots: mean_reward} over ok, scored rows for one model."""
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get("model") != model or not r.get("ok") or r.get("score") is None:
            continue
        by[r["task"]][int(r.get("shots", 0))].append(r["score"])
    return {t: {s: mean(v) for s, v in d.items() if v} for t, d in by.items()}


def influence_global(path):
    """task -> global% NLL reduction (letter-mmlu legs), the train-time transfer/learnability signal."""
    if not path or not Path(path).exists():
        return {}
    j = json.load(open(path)); base = j["baseline"]
    legs = ["bbh", "mmlu_math", "mmlu_logic", "mbpp", "fw", "dolci"]
    out = {}
    for t, rec in j.get("tasks", {}).items():
        if t.startswith("__"):
            continue
        vals = [-100.0 * rec[f"{l}_delta"] / base[f"{l}_nll"]
                for l in legs if base.get(f"{l}_nll") and rec.get(f"{l}_delta") is not None]
        if vals:
            out[t] = mean(vals)
    return out


def spearman(xs, ys):
    try:
        from scipy.stats import spearmanr
        rho, p = spearmanr(xs, ys)
        return rho, p
    except Exception:
        return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preds", default=str(DEFAULT_PREDS))
    ap.add_argument("--model", default=None, help="Base model to analyze (default: the most-covered one).")
    ap.add_argument("--influence", default=None, help="Influence JSON for the train-time signal correlation.")
    ap.add_argument("--out", default=str(ROOT / "task_diagnostics" / "SHOTS_LIFT.md"))
    args = ap.parse_args()

    rows = load_rows(args.preds)
    if args.model is None:                               # pick the model with the most multi-shot coverage
        cov = defaultdict(set)
        for r in rows:
            cov[r.get("model")].add(int(r.get("shots", 0)))
        args.model = max(cov, key=lambda m: (len(cov[m]), sum(1 for r in rows if r.get("model") == m)))
    rbs = reward_by_shots(rows, args.model)
    shots_seen = sorted({s for d in rbs.values() for s in d})
    if len(shots_seen) < 2:
        print(f"Only shots={shots_seen} present for {args.model}; run `zero_shot_eval.py --shots 1` (and 3) first.")
        return
    maxK = max(shots_seen)
    infl = influence_global(args.influence)

    lines = [f"# In-context learnability (ICL lift) — {args.model.split('/')[-1]}", "",
             "Reward = free-gen `score_answer` on the frozen model. **lift@K = reward@K − reward@0** — how "
             "much the model picks the task up from K worked examples (in-context learnability). "
             "Sorted by lift@" + str(maxK) + " (most ICL-learnable first).", "",
             "| task | " + " | ".join(f"{s}-shot" for s in shots_seen) +
             " | " + " | ".join(f"lift@{s}" for s in shots_seen if s) +
             (" | infl% |" if infl else " |"),
             "|" + "---|" * (1 + len(shots_seen) + sum(1 for s in shots_seen if s) + (1 if infl else 0))]

    tbl, pair_z, pair_i = [], [], []
    for t, d in rbs.items():
        r0 = d.get(0)
        if r0 is None or maxK not in d:
            continue
        liftK = d[maxK] - r0
        tbl.append((liftK, t, d))
        pair_z.append((r0, liftK))
        if t in infl:
            pair_i.append((infl[t], liftK))
    tbl.sort(reverse=True)
    for liftK, t, d in tbl:
        r0 = d[0]
        cells = [f"{d[s]:.2f}" if s in d else "—" for s in shots_seen]
        lifts = [f"{d[s]-r0:+.2f}" if s in d else "—" for s in shots_seen if s]
        row = f"| {t} | " + " | ".join(cells) + " | " + " | ".join(lifts)
        row += (f" | {infl[t]:+.1f} |" if t in infl else " | — |") if infl else " |"
        lines.append(row)

    lines.append("")
    if len(pair_z) >= 4:
        rho, p = spearman([a for a, _ in pair_z], [b for _, b in pair_z])
        if rho is not None:
            lines.append(f"- **Spearman(zero-shot reward, lift@{maxK}) = {rho:+.2f}** (p={p:.3f}, n={len(pair_z)}) "
                         "— negative ⇒ ICL helps most where zero-shot is weakest (headroom effect).")
    if len(pair_i) >= 4:
        rho, p = spearman([a for a, _ in pair_i], [b for _, b in pair_i])
        if rho is not None:
            lines.append(f"- **Spearman(train-time influence global%, lift@{maxK}) = {rho:+.2f}** (p={p:.3f}, "
                         f"n={len(pair_i)}) — positive ⇒ tasks that are learnable *in context* are also the "
                         "ones useful when *trained on* (two learnability probes agree).")
    text = "\n".join(lines) + "\n"
    Path(args.out).write_text(text)
    print(text)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
