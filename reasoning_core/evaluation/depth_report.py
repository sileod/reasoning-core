"""Per-depth reading of a battery's per-item scores: chance-adjusted, options-only-controlled, calibrated.

A leg mean hides what depth probes are for. This splits every leg by a row field (``depth`` by
default; any field, dotted for nesting, e.g. ``audit.forced_chain``) and reports, per group:

- ``acc_adj``: chance-adjusted accuracy, the mean over items of (correct - 1/k) / (1 - 1/k). 0 is
  chance whatever the option count, 1 is perfect, so 3-object and 7-object BBH are on one scale.
- ``opt_acc`` / ``context_gain``: the leg's options-only twin (``<leg>_optonly``, same items, prompt
  replaced by a bare stem) scores option prior alone; accuracy above it is what the context bought.
- ``cal_acc`` / ``cal_own_acc`` (closed-label legs): each option's cost minus that label's prior. ``cal``
  takes the prior from the options-only twin (content-free calibration); ``cal_own`` from the label's
  mean cost over the leg's own items, which also removes the in-context label bias a bare stem does
  not show (SmolLM2-1.7B on ProverQA: the twin favours "Uncertain" by ~1 nat, the leg by ~2.5).
  A constant label-prior picker scores chance under ``cal_own``.
- ``margin`` (and ``cal_own_margin``): best distractor cost minus gold cost, in nats. Continuous, so a paired
  difference resolves shifts far below what accuracy on a few hundred items can (about 4-5 points at n=600).

``compare`` gives treatment-minus-baseline per group, paired by item, with a 95% interval and z; the battery
report gives it for accuracy and for margin.

    python -m reasoning_core.evaluation.depth_report \\
        --manifest reasoning_core/resources/batteries/reasoning_depth_v2.json \\
        --sidecar per_example/RUN/arm.json.gz [--baseline per_example/RUN/base.json.gz] [--by depth]
"""
import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

CLOSED_LABEL = ("proverqa", "clutrr")             # options are a fixed label set: calibrate
CONTROLS = ("synthworlds_real", "synthworlds_synthetic")   # knowledge-vs-reasoning control, not a depth probe
OPTONLY = "_optonly"


def field(row, path):
    for key in path.split("."):
        row = row.get(key) if isinstance(row, dict) else None
    return row


def _costs(scores, i):
    costs = (scores.get("costs") or [None] * (i + 1))[i]
    return None if costs is None else [float("inf") if c is None else c for c in costs]


def label_prior(rows, scores):
    """Mean cost per label text over the items that offer it."""
    sums = defaultdict(list)
    for i, row in enumerate(rows):
        costs = _costs(scores, i)
        for label, cost in zip(row["choices"], costs or ()):
            if cost != float("inf"):
                sums[label].append(cost)
    return {label: mean(values) for label, values in sums.items()}


def _margin(costs, gold):
    rest = [c for j, c in enumerate(costs) if j != gold and c != float("inf")]
    return min(rest) - costs[gold] if rest and costs[gold] != float("inf") else None


def item_scores(rows, scores, optonly=None, calibrate=False):
    """Per item: correct, chance-adjusted correct, and (when available) the options-only and calibrated versions."""
    priors = {}
    if calibrate:
        priors["cal_own"] = label_prior(rows, scores)
        priors["cal"] = label_prior(rows, optonly) if optonly and optonly.get("costs") else priors["cal_own"]
    out = []
    for i, row in enumerate(rows):
        pred = scores["prediction"][i]
        if pred is None:
            out.append(None)
            continue
        k, gold = len(row["choices"]), row["answer_idx"]
        adj = lambda correct: (correct - 1 / k) / (1 - 1 / k)
        item = {"correct": float(pred == gold)}
        item["adj"] = adj(item["correct"])
        if optonly and optonly["prediction"][i] is not None:
            item["opt"] = float(optonly["prediction"][i] == gold)
            item["opt_adj"] = adj(item["opt"])
        costs = _costs(scores, i)
        if costs and (margin := _margin(costs, gold)) is not None:
            item["margin"] = margin
        for key, prior in priors.items() if costs else ():
            shifted = [c - prior.get(label, 0.0) for c, label in zip(costs, row["choices"])]
            item[key] = float(min(range(k), key=shifted.__getitem__) == gold)
            item[f"{key}_adj"] = adj(item[key])
            if (margin := _margin(shifted, gold)) is not None:
                item[f"{key}_margin"] = margin
        out.append(item)
    return out


def _groups(rows, values, by):
    groups = defaultdict(list)
    for row, value in zip(rows, values):
        if value is not None:
            groups[json.dumps(field(row, by))].append(value)
    order = sorted(groups, key=lambda g: (g == "null", str(json.loads(g)).zfill(6)))
    return {**{g: groups[g] for g in order}, "all": [v for g in order for v in groups[g]]}


def leg_report(rows, scores, optonly=None, calibrate=False, by="depth"):
    """{group: summary} for one leg. ``scores`` is one leg of a per-example sidecar."""
    if "prediction" not in scores:                 # generation (score) or qa_nll (nll): plain mean per group
        key = "score" if "score" in scores else "nll"
        return {g: {"n": len(v), key: mean(v)} for g, v in _groups(rows, scores[key], by).items()}
    report = {}
    for group, items in _groups(rows, item_scores(rows, scores, optonly, calibrate), by).items():
        summary = {"n": len(items), "acc": mean(i["correct"] for i in items), "acc_adj": mean(i["adj"] for i in items)}
        for key in ("opt", "cal", "cal_own"):
            scored = [i for i in items if key in i]
            if scored:
                summary[f"{key}_acc"] = mean(i[key] for i in scored)
                summary[f"{key}_adj"] = mean(i[f"{key}_adj"] for i in scored)
        for key in ("margin", "cal_own_margin"):
            scored = [i[key] for i in items if key in i]
            if scored:
                summary[key] = mean(scored)
        if "opt_acc" in summary:
            summary["context_gain"] = summary["acc"] - summary["opt_acc"]
        report[group] = summary
    return report


def compare(rows, baseline, treatment, optonly=(None, None), calibrate=False, by="depth", metric="adj"):
    """Treatment minus baseline per group, paired by item, with a normal 95% interval.
    ``metric``: "adj" (chance-adjusted accuracy), "cal_adj" or "cal_own_adj" (calibrated, closed-label legs),
    "margin" or "cal_own_margin" (nats)."""
    base = item_scores(rows, baseline, optonly[0], calibrate)
    treat = item_scores(rows, treatment, optonly[1], calibrate)
    diffs = [t[metric] - b[metric] if b and t and metric in b and metric in t else None for b, t in zip(base, treat)]
    report = {}
    for group, values in _groups(rows, diffs, by).items():
        delta = mean(values)
        se = stdev(values) / len(values) ** 0.5 if len(values) > 1 else None
        report[group] = {"n": len(values), "delta": delta,
                         "ci95": None if se is None else [delta - 1.96 * se, delta + 1.96 * se],
                         "z": delta / se if se else None}
    return report


def battery_report(battery, sidecar, baseline=None, by="depth"):
    """Every primary leg of a loaded battery against a sidecar ({"legs": {name: scores}}); options-only twins
    feed their leg, closed-label legs are calibrated, controls are marked."""
    legs = sidecar["legs"]
    out = {}
    for leg in battery.legs:
        if leg.name.endswith(OPTONLY) or leg.name not in legs:
            continue
        rows = _rows(leg)
        twin = leg.name + OPTONLY
        calibrate = leg.name.startswith(CLOSED_LABEL)
        entry = {"kind": leg.kind, "role": "control" if leg.name in CONTROLS else "probe",
                 "groups": leg_report(rows, legs[leg.name], legs.get(twin), calibrate, by)}
        if baseline and leg.name in baseline["legs"]:
            base = baseline["legs"][leg.name]
            if "prediction" in base:
                pair = (rows, base, legs[leg.name], (baseline["legs"].get(twin), legs.get(twin)), calibrate, by)
                entry["delta"] = compare(*pair, "cal_own_adj" if calibrate else "adj")
                if base.get("costs") and legs[leg.name].get("costs"):
                    entry["delta_margin"] = compare(*pair, "cal_own_margin" if calibrate else "margin")
        out[leg.name] = entry
    return out


def _rows(leg):
    """The leg's rows exactly as the battery scored them (limit, then keep)."""
    rows = []
    with Path(leg.path).open() as file:
        for line in file:
            row = json.loads(line)
            if row.get("prompt") is not None and row.get("answer") is not None:
                rows.append(row)
            if leg.limit and len(rows) >= leg.limit:
                break
    return [rows[i] for i in leg.keep] if leg.keep is not None else rows


def _load(path):
    path = Path(path)
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_text())


def main():
    from reasoning_core.evaluation.battery import DATA_DIR, load_battery_manifest

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--sidecar", required=True, help="per-example sidecar of the arm (json or json.gz)")
    ap.add_argument("--baseline", help="sidecar of the baseline arm: adds paired deltas")
    ap.add_argument("--by", default="depth", help="row field to group by (dotted for nesting)")
    ap.add_argument("--data-dir", default=DATA_DIR)
    a = ap.parse_args()
    battery = load_battery_manifest(a.manifest, a.data_dir)
    print(json.dumps(battery_report(battery, _load(a.sidecar), a.baseline and _load(a.baseline), a.by), indent=1))


if __name__ == "__main__":
    main()
