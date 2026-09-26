"""Which cheap signals track a measured target: per-task profiles, rankings, a held-out fit.

A target is any {task: number} -- measured transfer, a solve rate, a synergy rank -- so this
names no evaluation pipeline. Every figure is a Spearman correlation, because transfer scores
are only ever compared by position. The combined fit is judged out of fold and against a
length-only baseline: a signal that merely restates prompt length is free without a judge.
"""
from __future__ import annotations

from collections import defaultdict
import math

import numpy as np
from scipy.stats import rankdata

LENGTHS = ("log_prompt_chars", "log_answer_chars")


def cell_profiles(rows):
    """{(task, level): {feature: value}}: each judge's dimensions and the two lengths,
    averaged over that cell's examples."""
    cells = defaultdict(lambda: defaultdict(list))
    for row in rows:
        if "prompt" not in row:
            continue
        cell = cells[(row["task"], row["level"])]
        cell["log_prompt_chars"].append(math.log(1 + len(row["prompt"])))
        cell["log_answer_chars"].append(math.log(1 + len(row["answer"])))
        for judge, values in (row.get("signals") or {}).items():
            for name, value in values.items():
                if value is not None:
                    cell[f"{judge}:{name}"].append(value)
    return {key: {k: sum(v) / len(v) for k, v in cell.items()} for key, cell in cells.items()}


def task_profiles(rows):
    """{task: {feature: value}}: each cell feature averaged over levels, its value at the
    lowest level, and its drop from lowest to highest level (how steep the ladder is)."""
    by_task = defaultdict(dict)
    for (task, level), features in cell_profiles(rows).items():
        by_task[task][level] = features
    profiles = {}
    for task, levels in by_task.items():
        means = dict(sorted(levels.items()))
        low, high = means[min(means)], means[max(means)]
        features = {}
        for key in {k for cell in means.values() for k in cell}:
            values = [cell[key] for cell in means.values() if key in cell]
            features[key] = sum(values) / len(values)
            if key not in LENGTHS and key in low and key in high and len(means) > 1:
                features[f"{key}@low"] = low[key]
                features[f"{key}:drop"] = low[key] - high[key]
        profiles[task] = features
    return profiles


def spearman(x, y):
    # Average ranks: a ladder's solve rates tie often (0%, 0%, 0%), and breaking ties by
    # position would score the order the rows happened to be listed in.
    rx, ry = rankdata(x), rankdata(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def rank_signals(profiles, targets):
    """[(feature, rho, n)], strongest first, over tasks with both a profile and a target."""
    ranked = []
    for feature in sorted({k for p in profiles.values() for k in p}):
        pairs = [(p[feature], targets[t]) for t, p in profiles.items()
                 if feature in p and targets.get(t) is not None]
        if len(pairs) >= 10:
            x, y = map(np.array, zip(*pairs))
            ranked.append((feature, spearman(x, y), len(pairs)))
    return sorted(ranked, key=lambda r: -abs(r[1]) if r[1] == r[1] else 0)


def residualised(profiles, targets, features=LENGTHS):
    """The target minus its least-squares fit on `features`: what those do not explain."""
    tasks = [t for t, p in profiles.items()
             if targets.get(t) is not None and all(f in p for f in features)]
    x = np.array([[1.0] + [profiles[t][f] for f in features] for t in tasks])
    y = np.array([targets[t] for t in tasks], dtype=float)
    return dict(zip(tasks, y - x @ np.linalg.lstsq(x, y, rcond=None)[0]))


def _ridge(x, y, ridge):
    """A predictor fitted on (x, y): standardised features, closed-form ridge."""
    mu, sd = x.mean(0), x.std(0) + 1e-9
    a = (x - mu) / sd
    w = np.linalg.solve(a.T @ a + ridge * np.eye(a.shape[1]), a.T @ (y - y.mean()))
    return lambda new: ((new - mu) / sd) @ w + y.mean()


def held_out_predictions(profiles, targets, features, *, folds=5, ridge=1.0, seed=0,
                         groups=None):
    """{key: out-of-fold prediction} over keys carrying every feature. `groups` maps a key
    to the unit kept whole across folds -- a cell's task -- so no task is both fitted and
    predicted."""
    keys = sorted(k for k, p in profiles.items()
                  if targets.get(k) is not None and all(f in p for f in features))
    units = sorted({(groups or {}).get(k, k) for k in keys}, key=str)
    if len(units) < 2 * folds:
        return {}
    order = np.random.default_rng(seed).permutation(len(units)) % folds
    fold_of = {unit: order[i] for i, unit in enumerate(units)}
    x = np.array([[profiles[k][f] for f in features] for k in keys])
    y = np.array([targets[k] for k in keys], dtype=float)
    fold = np.array([fold_of[(groups or {}).get(k, k)] for k in keys])
    predicted = np.empty_like(y)
    for k in range(folds):
        predicted[fold == k] = _ridge(x[fold != k], y[fold != k], ridge)(x[fold == k])
    return dict(zip(keys, predicted))


def held_out_fit(profiles, targets, features, **options):
    """Spearman of out-of-fold ridge predictions, and how many keys it covers."""
    predicted = held_out_predictions(profiles, targets, features, **options)
    if not predicted:
        return float("nan"), 0
    keys = list(predicted)
    return spearman(np.array([predicted[k] for k in keys]),
                    np.array([targets[k] for k in keys])), len(keys)


def report(rows, targets, *, top=20, judges=("jev",)):
    profiles = task_profiles(rows)
    lines = [f"{len(profiles)} profiled tasks, {sum(t in targets for t in profiles)} with a target"]
    lines += [f"  {rho:+.2f}  n={n:<4} {feature}"
              for feature, rho, n in rank_signals(profiles, targets)[:top]]
    lines.append("beyond prompt and answer length (target residualised on both):")
    lines += [f"  {rho:+.2f}  n={n:<4} {feature}"
              for feature, rho, n in rank_signals(profiles, residualised(profiles, targets))[:top]
              if feature not in LENGTHS]
    everything = sorted({k for p in profiles.values() for k in p})
    for label, chosen in [("lengths only", list(LENGTHS))] + [
            (f"{judge} + lengths", [f for f in everything
                                    if f.startswith(judge + ":") or f in LENGTHS])
            for judge in judges] + [("all", everything)]:
        rho, n = held_out_fit(profiles, targets, chosen)
        lines.append(f"held-out fit, {label:<16} rho {rho:+.2f} over {n} tasks "
                     f"({len(chosen)} features)")
    return "\n".join(lines)


def ladder(rows, measured, *, judge="jev", features=None):
    """Predicted solve rate for every profiled (task, level), calibrated on measured cells.

    `measured` is {(task, level): solve rate} from a real probe. Returns the predictions
    (out of fold where a cell was measured, so they can be checked; a full fit elsewhere)
    and how well the held-out ones track the measurement: across cells, within a task,
    and the direction of each task's ladder where the probe saw it move.
    """
    cells = cell_profiles(rows)
    features = features or sorted({k for p in cells.values() for k in p
                                   if k.startswith(judge + ":") or k in LENGTHS})
    usable = {k: p for k, p in cells.items() if all(f in p for f in features)}
    held = held_out_predictions(usable, measured, features, groups={k: k[0] for k in usable})
    train = [k for k in usable if measured.get(k) is not None]
    fit = _ridge(np.array([[usable[k][f] for f in features] for k in train]),
                 np.array([measured[k] for k in train], dtype=float), 1.0)
    predicted = {k: float(held[k]) if k in held else
                 float(fit(np.array([[p[f] for f in features]]))[0]) for k, p in usable.items()}
    by_task = defaultdict(list)
    for (task, level), value in held.items():
        by_task[task].append((level, value, measured[(task, level)]))
    within, agree, moved = [], 0, 0
    for points in by_task.values():
        points.sort()
        if len(points) >= 3 and len({m for *_, m in points}) > 1:
            within.append(spearman(np.array([v for _, v, _ in points]),
                                   np.array([m for *_, m in points])))
        if len(points) >= 2 and abs(points[0][2] - points[-1][2]) >= 0.25:
            moved += 1
            agree += (points[0][2] > points[-1][2]) == (points[0][1] > points[-1][1])
    within = [w for w in within if w == w]
    keys = list(held)
    stats = {"cells": len(keys),
             "cell_rho": spearman(np.array([held[k] for k in keys]),
                                  np.array([measured[k] for k in keys])) if keys else None,
             "within_task_rho": sum(within) / len(within) if within else None,
             "direction": f"{agree}/{moved}"}
    return predicted, stats
