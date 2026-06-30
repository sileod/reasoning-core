#!/usr/bin/env python
"""Summarize experiments/external_eval_results.csv into per-task influence
on HumanEval/CRUXEval relative to the no-aux `baseline` arm.

A positive delta means training on that synthetic task's aux data, on top of
main_data, beat training on main_data alone for that metric. This is the
"does this synthetic task actually transfer" signal for the paper — without
the baseline row this can't be computed at all.
"""
import argparse
import csv
import math
from pathlib import Path


METRICS = [
    "humaneval_pass@1", "humaneval_pass@5", "humaneval_pass@10",
    "cruxeval_o_acc", "cruxeval_i_acc",
]


def to_float(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results_file", default="experiments/external_eval_results.csv")
    parser.add_argument("--baseline_label", default="baseline")
    parser.add_argument("--out", default=None,
                         help="Optional path to also write the summary as Markdown.")
    args = parser.parse_args()

    path = Path(args.results_file)
    if not path.exists():
        raise SystemExit(f"{path} does not exist yet — run evaluate_external.py first.")

    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    if not rows:
        raise SystemExit(f"{path} has no rows.")

    # Keep only the LATEST row per trained_task, so re-running an arm
    # supersedes its earlier result instead of being averaged with it.
    latest = {}
    for r in rows:
        latest[r["trained_task"]] = r
    rows = list(latest.values())

    baseline = latest.get(args.baseline_label)
    if baseline is None:
        print(f"warning: no '{args.baseline_label}' row found yet — showing raw scores only, no deltas.")

    present_metrics = [m for m in METRICS if any(to_float(r.get(m)) is not None for r in rows)]

    table = []
    for r in rows:
        task = r["trained_task"]
        if task == args.baseline_label:
            continue
        line = {"task": task}
        n_positive = 0
        n_scored = 0
        for m in present_metrics:
            val = to_float(r.get(m))
            base_val = to_float(baseline.get(m)) if baseline else None
            line[m] = val
            if val is not None and base_val is not None:
                delta = val - base_val
                ratio = delta / base_val if base_val else float("nan")
                line[f"{m}_delta"] = delta
                line[f"{m}_ratio"] = ratio
                n_scored += 1
                n_positive += delta > 0
        line["positive_ratio"] = n_positive / n_scored if n_scored else float("nan")
        table.append(line)

    table.sort(key=lambda l: (-l["positive_ratio"] if math.isfinite(l["positive_ratio"]) else math.inf, l["task"]))

    header = ["task"] + present_metrics + [f"{m}_delta" for m in present_metrics] + ["positive_ratio (frac of metrics improved over baseline)"]
    print(" | ".join(header))
    for line in table:
        cells = [line["task"]]
        cells += [f"{line.get(m, float('nan')):.4f}" if line.get(m) is not None else "" for m in present_metrics]
        cells += [f"{line.get(f'{m}_delta', float('nan')):+.4f}" if line.get(f"{m}_delta") is not None else "" for m in present_metrics]
        pr = line["positive_ratio"]
        cells += [f"{pr:.2f}" if math.isfinite(pr) else "n/a"]
        print(" | ".join(cells))

    if args.out:
        lines = ["# External Benchmark Influence", ""]
        if baseline:
            lines.append(f"Baseline (`{args.baseline_label}`) scores: " + ", ".join(
                f"{m}={to_float(baseline.get(m))}" for m in present_metrics if to_float(baseline.get(m)) is not None
            ))
            lines.append("")
        lines.append("Positive delta = beat the no-aux baseline on that metric.")
        lines.append("")
        cols = ["task"] + present_metrics + [f"{m}_delta" for m in present_metrics] + ["positive_ratio"]
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("|" + "|".join("---" for _ in cols) + "|")
        for line in table:
            row_cells = [line["task"]]
            row_cells += [f"{line.get(m):.4f}" if line.get(m) is not None else "" for m in present_metrics]
            row_cells += [f"{line.get(f'{m}_delta'):+.4f}" if line.get(f"{m}_delta") is not None else "" for m in present_metrics]
            pr = line["positive_ratio"]
            row_cells += [f"{pr:.2f}" if math.isfinite(pr) else "n/a"]
            lines.append("| " + " | ".join(row_cells) + " |")
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text("\n".join(lines) + "\n")
        print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()