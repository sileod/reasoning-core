"""Numeric mutation of table_statistics: the same labelled numeric tables in the same renderings, but instead of
naming the column or row a statistic selects, compute a group statistic in plain words -- a group mean, the gap
between two group means, a within-group range, a sum over two groups, or a count of rows where one column
exceeds another. Values are small integers; means are asked rounded to one decimal, so answers stay short.
"""
import random
import string
from dataclasses import dataclass

import pandas as pd

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding as sround
from reasoning_core.tasks.table_qa import STAT_RENDERERS, get_renderers, sample_renderer


@dataclass
class TableGroupStatsConfig(Config):
    n_rows: float = 6
    n_numeric: float = 2
    n_groups: float = 2
    magnitude: float = 9

    def apply_difficulty(self, level):
        self.n_rows += 2.5 * level
        self.n_numeric += 0.5 * level
        self.n_groups += 0.4 * level
        self.magnitude += 6 * level


def _tenths(x):
    """x rounded to one decimal, or None on a rounding tie (x.x5 exactly)."""
    t = x * 10
    return None if abs(abs(t - int(t)) - 0.5) < 1e-9 else f"{round(t) / 10:.1f}"


def _question(rng, df, labels, cols):
    x, y = rng.sample(cols, 2) if len(cols) > 1 else (cols[0], None)
    a, b = rng.sample(labels, 2)
    ga, gb = df[df.label == a][x], df[df.label == b][x]
    ops = ["mean", "gap", "range", "sum"] + (["count"] if y else [])
    op = rng.choice(ops)
    if op == "mean" and len(ga):
        return f"What is the mean of {x} over rows labelled {a}?", _tenths(ga.mean()), "tenths"
    if op == "gap" and len(ga) and len(gb) and ga.mean() != gb.mean():
        a, b, ga, gb = (a, b, ga, gb) if ga.mean() > gb.mean() else (b, a, gb, ga)
        return (f"By how much does the mean of {x} for rows labelled {a} exceed that for rows labelled {b}?",
                _tenths(ga.mean() - gb.mean()), "tenths")
    if op == "range" and len(ga) > 1:
        return f"What is the range (maximum minus minimum) of {x} over rows labelled {a}?", str(ga.max() - ga.min()), "int"
    if op == "sum" and len(ga) and len(gb):
        return f"What is the sum of {x} over rows labelled {a} or {b}?", str(ga.sum() + gb.sum()), "int"
    if op == "count" and len(ga):
        rows = df[df.label == a]
        return f"In how many rows labelled {a} is {x} greater than {y}?", str(int((rows[x] > rows[y]).sum())), "int"
    return None, None, None


class TableGroupStats(DevTask):
    summary = ("Compute a group statistic over a labelled integer table rendered in varied formats: a group mean or "
               "the gap between two group means (one decimal), a within-group range, a sum over two groups, or a "
               "count of rows where one column exceeds another; the numeric twin of table_statistics.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or TableGroupStatsConfig())

    def generate_entry(self):
        c, rng = self.config, random
        while True:
            cols = rng.sample(string.ascii_uppercase, max(1, sround(c.n_numeric)))
            labels = [f"L{i}" for i in range(max(2, sround(c.n_groups)))]
            m = max(3, sround(c.magnitude))
            n = max(4, sround(c.n_rows))
            df = pd.DataFrame({"label": [rng.choice(labels) for _ in range(n)],
                               **{x: [rng.randint(-m, m) for _ in range(n)] for x in cols}})
            question, answer, kind = _question(rng, df, labels, cols)
            if answer is None:
                continue
            fmt = sample_renderer(STAT_RENDERERS)
            table = get_renderers(df.astype(object))[fmt](index=False)
            return Entry({"table": table, "question": question, "kind": kind, "table_format": fmt}, answer)

    def render_prompt(self, m):
        how = "a number rounded to one decimal, such as 2.0" if m["kind"] == "tenths" else "an integer"
        return f"{m['table']}\n\n{m['question']} Answer with {how}."

    def score_answer(self, answer, entry):
        try:
            got = float(str(answer).strip().rstrip("."))
        except ValueError:
            return 0.0
        return float(abs(got - float(entry.answer)) < 1e-9)
