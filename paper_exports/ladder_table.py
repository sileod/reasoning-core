#!/usr/bin/env python3
"""ladder_table.py — HIGHLIGHT steps-ladder data for the best model.

Reads influence_COLL-<coll>_<TAG>_S*_T<T>_M<mix>_<main>_pretrained.json across a STEPS ladder and emits,
per training-step count, comparable reasoning curves for: base (pretrained_only, step 0), the main-only
control (baseline), and each collection arm. Lower reasoning-NLL = better. Output = table (steps x series)
so the curve can be plotted any way later. Also prints %NLL-red of each collection vs the main-only control.

Usage: python paper_exports/ladder_table.py --tag HLOLMO --main dolci --mix 20 --steps 300,600,1200,2400
"""
import argparse, glob, json
from pathlib import Path
from statistics import mean

PR = Path(__file__).resolve().parent.parent / "per_task_results"
OUT = Path(__file__).resolve().parent
REASON = ["bbh", "mmlu_math_cloze", "mmlu_logic_cloze"]


def rmean(d, src):
    """mean reasoning-NLL over legs from a sub-dict (baseline / pretrained_only / arm)."""
    sub = d.get(src)
    if not sub: return None                    # null baseline (partial/preempted write) → skip, don't crash
    vs = [sub.get(l + "_nll") for l in REASON]
    vs = [v for v in vs if v is not None]
    return mean(vs) if vs else None


def collect(tag, main, mix, T, colls, seed="*"):
    """{series: nll} for one step count, seed-averaged. series = base | main-only | <coll>.
    seed='*' averages all seeds; pass a specific seed (e.g. 45) for a clean single-seed curve
    (needed when different seeds populate different step counts → seed-avg would confound the trend)."""
    base, ctrl, arms = [], [], {c: [] for c in colls}
    for c in colls:
        for f in glob.glob(str(PR / f"influence_COLL-{c}_{tag}_S{seed}_T{T}_M{mix}_{main}_pretrained.json")):
            d = json.loads(Path(f).read_text())
            if "pretrained_only" in d and rmean(d, "pretrained_only") is not None:
                base.append(rmean(d, "pretrained_only"))
            if rmean(d, "baseline") is not None:
                ctrl.append(rmean(d, "baseline"))
            a = (d.get("tasks") or {}).get("__COLLECTION__")
            if a:
                vs = [a.get(l + "_nll") for l in REASON]; vs = [v for v in vs if v is not None]
                if vs:
                    arms[c].append(mean(vs))
    row = {"base": mean(base) if base else None, "main-only": mean(ctrl) if ctrl else None}
    for c in colls:
        row[c] = mean(arms[c]) if arms[c] else None
    return row


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="HLOLMO")
    ap.add_argument("--main", default="dolci")
    ap.add_argument("--mix", type=int, default=20)
    ap.add_argument("--steps", default="300,600,1200,2400")
    ap.add_argument("--seed", default="*", help="'*' = seed-avg (default); a number = single-seed clean curve")
    a = ap.parse_args()
    Ts = [int(x) for x in a.steps.split(",")]
    colls = ["rc", "rgym", "synlogic", "pw"]
    series = ["base", "main-only"] + colls
    grid = {T: collect(a.tag, a.main, a.mix, T, colls, a.seed) for T in Ts}

    _seedlbl = "seed-avg" if a.seed == "*" else f"seed {a.seed}"
    print(f"REASONING-NLL vs STEPS  (model tag {a.tag}, background={a.main}, mix {a.mix}%, {_seedlbl}; lower=better)")
    print("series      " + "".join(f"T{T:<8}" for T in Ts))
    for s in series:
        print(f"{s:11s} " + "".join((f"{grid[T][s]:<9.4f}" if grid[T].get(s) is not None else "--       ") for T in Ts))
    print("\n%NLL-red vs main-only control  (+ = aux beats dolci-only at that step count)")
    for c in colls:
        cells = []
        for T in Ts:
            b, arm = grid[T].get("main-only"), grid[T].get(c)
            cells.append(f"{(b-arm)/b*100:+.2f}" if (b and arm) else "--")
        print(f"  {c:9s} " + "  ".join(f"{x:>7s}" for x in cells))
    rows = [f"{s}," + ",".join(str(grid[T].get(s, "")) for T in Ts) for s in series]
    (OUT / "ladder.csv").write_text("series," + ",".join(f"T{T}" for T in Ts) + "\n" + "\n".join(rows) + "\n")
    print(f"\n-> wrote {OUT/'ladder.csv'}")
