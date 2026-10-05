"""Compare existing menu/no-menu legs on identical items, without rebuilding data.

Example:
    python scripts/report_format_controls.py per_task_results/*CMPSTD360M*.json \
        --sidecars-root per_example --output /tmp/format-controls.json

The contrast is treatment-minus-baseline with a menu, minus the same effect without
the menu. Only items whose prompts actually differ contribute to that contrast.
"""
import argparse
from collections import defaultdict, deque
import gzip
import json
import math
from pathlib import Path
import re
from statistics import mean, stdev


MENU = re.compile(r"(?is)\n\s*options?\s*:.*$")
PAIRS = (("bbh_dev_cloze", "bbh_dev_nomenu"),
         ("bbh_test_cloze", "bbh_test_nomenu"),
         ("mmlu_math_cloze", "mmlu_math_nomenu"))


def item_key(row):
    choices = tuple(str(c).strip() for c in row["choices"])
    gold = int(row["answer_idx"])
    if not 0 <= gold < len(choices):
        raise ValueError("Invalid gold choice index")
    return MENU.sub("", row["prompt"]).rstrip(), choices, gold


def match_items(source, target):
    """One-to-one join preserving duplicate occurrences and candidate order."""
    available = defaultdict(deque)
    for index, row in enumerate(target):
        if len(row.get("choices", ())) >= 2:
            available[item_key(row)].append(index)
    matched = []
    for index, row in enumerate(source):
        if len(row.get("choices", ())) >= 2 and available[item_key(row)]:
            matched.append((index, available[item_key(row)].popleft()))
    return matched


def estimate(values):
    if not values:
        return {"items": 0, "mean": None, "ci95": None}
    average = mean(values)
    interval = None
    if len(values) > 1:
        error = 1.96 * stdev(values) / len(values) ** 0.5
        interval = [average - error, average + error]
    return {"items": len(values), "mean": average, "ci95": interval}


def contrast(source, target, baseline, treatment, source_name, target_name):
    matched = match_items(source, target)
    changed = [(i, j) for i, j in matched
               if source[i]["prompt"].rstrip() != target[j]["prompt"].rstrip()]
    report = {"source": source_name, "target": target_name,
              "source_items": len(source), "target_items": len(target),
              "matched_items": len(matched), "changed_prompt_items": len(changed)}
    if not changed:
        return {**report, "status": "no matched format change"}
    for name, rows in ((source_name, source), (target_name, target)):
        for sidecar in (baseline, treatment):
            for key in ("prediction", "margin"):
                if len(sidecar[name][key]) != len(rows):
                    raise ValueError(f"{name}: sidecar and frozen item counts differ")
    effects = {"accuracy_pp": [], "margin": []}
    transfer = {name: {"accuracy_pp": [], "margin": []}
                for name in (source_name, target_name)}
    for i, j in changed:
        gold = int(source[i]["answer_idx"])
        for metric, key in (("accuracy_pp", "prediction"), ("margin", "margin")):
            bm, tm = baseline[source_name][key][i], treatment[source_name][key][i]
            bn, tn = baseline[target_name][key][j], treatment[target_name][key][j]
            if any(v is None for v in (bm, tm, bn, tn)):
                continue
            if metric == "accuracy_pp":
                bm, tm, bn, tn = [100 * int(v == gold) for v in (bm, tm, bn, tn)]
            transfer[source_name][metric].append(tm - bm)
            transfer[target_name][metric].append(tn - bn)
            effects[metric].append((tm - bm) - (tn - bn))
    return {**report, "status": "paired format contrast",
            "transfer_on_matched_items": {
                name: {metric: estimate(values) for metric, values in metrics.items()}
                for name, metrics in transfer.items()},
            "menu_effect_on_transfer": {k: estimate(v) for k, v in effects.items()}}


def find_sidecar(sidecars, metrics, battery_id, seed):
    def equal(left, right):
        return left == right or (isinstance(left, (int, float))
                                 and isinstance(right, (int, float))
                                 and math.isclose(left, right, abs_tol=1e-8))
    matches = [s for s in sidecars if s.get("battery_id") == battery_id
               and s.get("seed") == seed and s.get("metrics") and all(
        k in metrics and equal(v, metrics[k]) for k, v in s["metrics"].items())]
    if len(matches) != 1:
        raise ValueError(f"Expected one matching battery sidecar, found {len(matches)}")
    return matches[0]["legs"]


def load_rows(leg, data_dir):
    from reasoning_core.evaluation.metrics import load_eval_suite

    suite = load_eval_suite(data_dir / leg["path"], "", limit=leg.get("limit"),
                            keep=leg.get("keep"))
    return [{"prompt": e.prompt, "answer": e.answer, "choices": e.choices,
             "answer_idx": e.answer_index} for e in suite.examples]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cells", nargs="+", type=Path)
    parser.add_argument("--sidecars-root", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, default=Path("data_cache"))
    parser.add_argument("--manifest", type=Path,
                        default=Path("reasoning_core/resources/batteries/copyfree_battery_v8.json"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pair", nargs=2, action="append", metavar=("MENU", "NOMENU"),
                        help="Leg pair to compare; repeat for multiple pairs")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    legs = {leg["name"]: leg for leg in json.loads(args.manifest.read_text())["legs"]}
    pairs = args.pair or PAIRS
    rows = {name: load_rows(legs[name], args.data_dir) for pair in pairs for name in pair}
    from reasoning_core.evaluation.battery import load_battery_manifest

    battery_ids = {}
    report = {"contrast": "(treatment-baseline)_menu - (treatment-baseline)_nomenu",
              "uncertainty": "paired item normal intervals per seed; no seed-level inference",
              "cells": []}
    for path in args.cells:
        cell = json.loads(path.read_text())
        length = cell["max_length"]
        if length not in battery_ids:
            battery_ids[length] = load_battery_manifest(
                args.manifest, args.data_dir, length).identifier
        if cell["battery_id"] != battery_ids[length]:
            raise ValueError(f"{path}: frozen battery identity does not match the cell")
        if not cell.get("per_example_dir"):
            raise ValueError(f"{path}: per_example_dir is missing")
        directory = args.sidecars_root / Path(cell["per_example_dir"]).name
        sidecars = []
        for p in directory.glob("*.json.gz"):
            if "__ds_" not in p.name:
                with gzip.open(p, "rt") as file:
                    sidecars.append(json.load(file))
        baseline = find_sidecar(sidecars, cell["baseline"], cell["battery_id"], cell["seed"])
        for task, metrics in cell["tasks"].items():
            treatment = find_sidecar(sidecars, metrics, cell["battery_id"], cell["seed"])
            report["cells"].append({"path": str(path), "task": task, "seed": cell["seed"],
                                    "pairs": [contrast(rows[a], rows[b], baseline, treatment, a, b)
                                              for a, b in pairs]})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
