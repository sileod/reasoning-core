#!/usr/bin/env python
"""CHEAP-PREDICTOR PANEL (analysis, GPU-free) — which instant/cheap signals forecast the slow per-task
GPU influence? Correlates each cheap signal against the expensive influence (global% + bbh%).

Cheap signals, by cost:
  FREE/instant (from the few-shot preds' stored prompt+gold): mean answer chars, mean prompt chars.
  API-solve (from shots_preds.jsonl): zero-shot reward, reward@3, ICL lift@3 = r@3 − r@0.
  API-judge (from task_ratings.jsonl): LLM data-quality ratings (interestingness, diversity,
            reasoning_depth, difficulty, learnability, training_usefulness).

Target (expensive, GPU): per-task influence global% and bbh% from a reference influence JSON.

  python task_diagnostics/cheap_predictors.py --model openrouter/meta-llama/llama-3.3-70b-instruct \
      --influence per_task_results/influence_LOCAL_bbf7208274_S43_T300_M20_fwdolci_pretrained.json
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
JUDGE_AXES = ["interestingness", "diversity", "reasoning_depth", "difficulty",
              "learnability", "training_usefulness"]


def influence(path):
    j = json.load(open(path)); base = j["baseline"]
    legs = ["bbh", "mmlu_math", "mmlu_logic", "mbpp", "fw", "dolci"]
    g, b = {}, {}
    for t, rec in j.get("tasks", {}).items():
        if t.startswith("__"):
            continue
        vs = [-100.0 * rec[f"{l}_delta"] / base[f"{l}_nll"]
              for l in legs if base.get(f"{l}_nll") and rec.get(f"{l}_delta") is not None]
        if vs:
            g[t] = mean(vs)
        if base.get("bbh_nll") and rec.get("bbh_delta") is not None:
            b[t] = -100.0 * rec["bbh_delta"] / base["bbh_nll"]
    return g, b


def solve_signals(preds_path, model):
    """task -> dict(zs_reward, r3, lift3, ans_chars, prompt_chars) from the shots preds."""
    by = defaultdict(lambda: defaultdict(list))          # task -> shots -> [score]
    lens = defaultdict(lambda: ([], []))                 # task -> (ans_chars[], prompt_chars[])
    for line in Path(preds_path).read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("model") != model:
            continue
        sh = int(r.get("shots", 0))
        if r.get("ok") and r.get("score") is not None:
            by[r["task"]][sh].append(r["score"])
        if sh == 0:                                      # length from the bare (0-shot) examples
            lens[r["task"]][0].append(len(str(r.get("gold", ""))))
            lens[r["task"]][1].append(len(str(r.get("prompt", ""))))
    out = {}
    for t, d in by.items():
        zs = mean(d[0]) if d.get(0) else None
        r3 = mean(d[3]) if d.get(3) else None
        rec = {"zs_reward": zs, "r3": r3,
               "lift3": (r3 - zs) if (zs is not None and r3 is not None) else None,
               "ans_chars": mean(lens[t][0]) if lens[t][0] else None,
               "prompt_chars": mean(lens[t][1]) if lens[t][1] else None}
        out[t] = rec
    return out


def judge_signals(path, model=None):
    """task -> {axis: score}. If multiple rows/task, mean them."""
    if not Path(path).exists():
        return {}
    acc = defaultdict(lambda: defaultdict(list))
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if model and r.get("model") != model:
            continue
        sc = r.get("scores") or {}
        for a in JUDGE_AXES:
            if sc.get(a) is not None:
                acc[r["task"]][a].append(sc[a])
    return {t: {a: mean(v) for a, v in d.items()} for t, d in acc.items()}


def spearman(xs, ys):
    try:
        from scipy.stats import spearmanr
        return spearmanr(xs, ys)
    except Exception:
        return (None, None)


def corr(sig_map, target_map):
    common = sorted(set(sig_map) & set(target_map))
    xs = [sig_map[t] for t in common if sig_map[t] is not None and target_map[t] is not None]
    ys = [target_map[t] for t in common if sig_map[t] is not None and target_map[t] is not None]
    if len(xs) < 5:
        return (None, None, len(xs))
    rho, p = spearman(xs, ys)
    return (rho, p, len(xs))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--influence", required=True)
    ap.add_argument("--preds", default=str(ROOT / "task_diagnostics" / "shots_preds.jsonl"))
    ap.add_argument("--ratings", default=str(ROOT / "task_diagnostics" / "task_ratings.jsonl"))
    ap.add_argument("--model", default="openrouter/meta-llama/llama-3.3-70b-instruct")
    ap.add_argument("--out", default=str(ROOT / "task_diagnostics" / "CHEAP_PREDICTORS.md"))
    args = ap.parse_args()

    g, b = influence(args.influence)
    sol = solve_signals(args.preds, args.model)
    jud = judge_signals(args.ratings)

    # assemble per-signal task->value maps
    signals = {}
    for key in ["zs_reward", "r3", "lift3", "ans_chars", "prompt_chars"]:
        signals[key] = {t: sol[t][key] for t in sol if sol[t].get(key) is not None}
    for a in JUDGE_AXES:
        m = {t: jud[t][a] for t in jud if a in jud[t]}
        if m:
            signals[f"judge_{a}"] = m

    rows = []
    for name, m in signals.items():
        rg, pg, ng = corr(m, g)
        rb, pb, nb = corr(m, b)
        rows.append((name, rg, pg, ng, rb, pb, nb))
    rows.sort(key=lambda r: -(abs(r[1]) if r[1] is not None else -1))

    L = [f"# Cheap predictors of GPU influence — model {args.model.split('/')[-1]}", "",
         "Each cheap signal's Spearman ρ vs the expensive per-task influence "
         "(`global%` = mean 6-leg NLL reduction; `bbh%`). Ranked by |ρ vs global|. "
         "Positive ρ ⇒ higher signal predicts more-useful task.", "",
         "| cheap signal | ρ(global) | p | n | ρ(bbh) | p | n |",
         "|:--|--:|--:|--:|--:|--:|--:|"]
    def f(x, d=2): return f"{x:+.{d}f}" if x is not None else "—"
    for name, rg, pg, ng, rb, pb, nb in rows:
        L.append(f"| {name} | {f(rg)} | {f(pg,3) if pg is not None else '—'} | {ng} | "
                 f"{f(rb)} | {f(pb,3) if pb is not None else '—'} | {nb} |")
    L += ["", "_zs_reward=zero-shot reward, r3=reward@3-shot, lift3=ICL lift (r3−r0), ans/prompt_chars="
          "answer/prompt length, judge_*=LLM data-quality rating axis._"]
    text = "\n".join(L) + "\n"
    Path(args.out).write_text(text)
    print(text)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
