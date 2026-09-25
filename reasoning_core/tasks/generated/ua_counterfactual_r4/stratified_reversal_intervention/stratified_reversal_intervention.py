"""Stratified reversal intervention: flip a pooled comparison with minimal ops
that preserve within-stratum cell orderings."""

import random
import itertools
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'stratified_reversal_intervention (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_counterfactual_r4/stratified_reversal_intervention',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Answer form is a canonical sequence of operations like M2:r1c2+1,D3:r2c1,R4:r1c3, each op specified by stratum, row, column, and delta; impossibility is the literal string IMPOSSIBLE."

IMPOSSIBLE = "IMPOSSIBLE"


@dataclass
class StratifiedReversalConfig(Config):
    strata: int = 2
    rows: int = 2
    cols: int = 2
    delta_max: int = 1
    max_ops: int = 3

    def apply_difficulty(self, level):
        self.strata = 2 + (level // 3)
        self.rows = 2 + (level % 2)
        self.cols = 2 + (level % 2)
        self.delta_max = 1 + (level // 3)
        self.max_ops = 2 + (level // 2)


def _cells(tables):
    """Yield (stratum, row, col, value) in deterministic order."""
    out = []
    for s, t in enumerate(tables):
        for r, row in enumerate(t):
            for c, val in enumerate(row):
                out.append((s, r, c, val))
    return out


def _format_op(s, r, c, delta):
    if delta >= 0:
        return f"M{s}:r{r + 1}c{c + 1}+{delta}"
    return f"D{s}:r{r + 1}c{c + 1}-{-delta}"


def _format_ops(ops):
    keyed = sorted((s, r, c, delta) for s, r, c, delta in ops)
    return ",".join(_format_op(s, r, c, d) for s, r, c, d in keyed)


def _apply(tables, ops):
    newt = [[row[:] for row in t] for t in tables]
    for s, r, c, delta in ops:
        newt[s][r][c] += delta
    return newt


def _valid(tables, baseline_tables):
    """Check non-negativity and preserved within-stratum ordering."""
    for s in range(len(tables)):
        t = tables[s]
        b = baseline_tables[s]
        r = len(t)
        cl = len(t[0])
        cells_new = [t[i][j] for i in range(r) for j in range(cl)]
        cells_base = [b[i][j] for i in range(r) for j in range(cl)]
        for v in cells_new:
            if v < 0:
                return False
        for a in range(len(cells_base)):
            for bb in range(len(cells_base)):
                if cells_base[a] < cells_base[bb] and cells_new[a] > cells_new[bb]:
                    return False
    return True


def _pooled(tables):
    return sum(val for _s, _r, _c, val in _cells(tables))


def _search(tables, baseline_tables, need, direction, delta_max, max_ops):
    """Return min number of ops (list of (s,r,c,delta)) flip, or None."""
    if need <= 0:
        return []
    ncells = len(_cells(tables))
    if ncells * delta_max < need:
        return None
    # candidate single ops of each magnitude in the needed direction
    candidates = []
    for s, r, c, val in _cells(baseline_tables):
        for m in range(1, delta_max + 1):
            delta = direction * m
            single_tables = _apply(baseline_tables, [(s, r, c, delta)])
            if _valid(single_tables, baseline_tables):
                candidates.append((s, r, c, delta))
    if not candidates:
        return None
    # deterministic candidate ordering
    candidates = [c for c in candidates]
    cand_by_direction = [c for c in candidates if c[3] == direction * delta_max]
    for k in range(1, max_ops + 1):
        best = _search_k(baseline_tables, candidates, k, need, direction, delta_max,
                         cand_by_direction)
        if best is not None:
            return best
    return None


def _search_k(baseline_tables, candidates, k, need, direction, delta_max, cand_by_direction):
    """Try to find a valid set of exactly k ops (distinct cells) achieving need."""
    # prefer max-magnitude ops first for efficiency of reaching need, but must be valid
    if k * delta_max < need:
        return None
    best = None
    n = len(candidates)
    for combo in itertools.combinations(range(n), k):
        ops = [candidates[i] for i in combo]
        cells = [(c[0], c[1], c[2]) for c in ops]
        if len(set(cells)) != k:
            continue
        total = sum(c[3] for c in ops)
        if direction > 0 and total < need:
            continue
        if direction < 0 and total > -need:
            continue
        newt = _apply(baseline_tables, ops)
        if _valid(newt, baseline_tables):
            return ops
    return best


def _gen_tables(cfg):
    while True:
        tables = []
        for _ in range(cfg.strata):
            t = [[random.randint(0, 3) for _ in range(cfg.cols)] for _ in range(cfg.rows)]
            tables.append(t)
        return tables


def _make_threshold(tables, delta_max, max_ops, imp_prob):
    """Pick a threshold; returns (threshold, direction, need) where direction
    is +1 to raise the pooled total and -1 to lower it."""
    capacity = len(_cells(tables)) * delta_max
    if random.random() < imp_prob:
        # guaranteed unreachable -> IMPOSSIBLE
        need = capacity + 1
    else:
        need = random.randint(1, max(1, min(max_ops, capacity)))
    direction = random.choice((1, -1))
    pooled = _pooled(tables)
    threshold = pooled + direction * need
    return threshold, direction, need


class StratifiedReversalIntervention(Task):
    summary = ("Move, delete or duplicate permitted records in stratified count tables; find the smallest intervention "
               "reversing the pooled comparison while preserving every within-stratum ordering, or report impossibility.")
    config_cls = StratifiedReversalConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(60):
            tables = _gen_tables(cfg)
            pooled = _pooled(tables)
            threshold, direction, need = _make_threshold(tables, cfg.delta_max,
                                                         cfg.max_ops, 0.18)
            ops = _search(tables, tables, need, direction, cfg.delta_max, cfg.max_ops)
            if ops is not None:
                newt = _apply(tables, ops)
                if (_pooled(newt) >= threshold) == (pooled >= threshold):
                    continue
                if not _valid(newt, tables):
                    continue
                answer = _format_ops(ops)
            else:
                # no solution within op budget -> impossible
                answer = IMPOSSIBLE
            baseline_repr = [[row[:] for row in t] for t in tables]
            metadata = {
                "tables": baseline_repr,
                "threshold": threshold,
                "pooled": pooled,
                "delta_max": cfg.delta_max,
                "max_ops": cfg.max_ops,
                "ops": ops,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not construct a valid instance")

    def render_prompt(self, metadata):
        lines = []
        for s, t in enumerate(metadata["tables"]):
            rows = "; ".join("[" + ", ".join(str(v) for v in row) + "]" for row in t)
            lines.append(f"Stratum {s}: {rows}")
        return (
            "You have stratified count tables (each stratum is a grid of non-negative integers). "
            "The pooled total is the sum of every cell across all strata. "
            f"The current pooled total is {metadata['pooled']}; the comparison of interest is "
            f"whether the pooled total is at least the threshold {metadata['threshold']}.\n"
            + "\n".join(lines)
            + "\n\nAn operation changes one cell of one stratum by an integer delta (M/+ means records "
            "added, D/- means records removed). A valid intervention must keep every cell non-negative "
            "and preserve every within-stratum ordering: no two cells in the same stratum that were "
            "strictly ordered may end up strictly reversed (equal values may reorder freely). "
            "Find the SMALLEST intervention (fewest operations) that flips the pooled comparison "
            f"(makes 'total >= {metadata['threshold']}' change from true to false or false to true). "
            "Each operation may change a cell by at most "
            f"{metadata['delta_max']} in magnitude, and at most {metadata['max_ops']} operations are permitted.\n"
            "Answer as a comma-separated canonical sequence of operations, each of the form "
            "M{stratum}:r{row}c{column}+{delta} (for an increase) or D{stratum}:r{row}c{column}-{delta} "
            "(for a decrease), rows and columns are 1-indexed, e.g. M0:r1c2+1,D1:r2c1-2. "
            "If no valid intervention exists, answer exactly IMPOSSIBLE."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        answer = answer.strip()
        if entry.answer == IMPOSSIBLE:
            return 1.0 if answer == IMPOSSIBLE else 0.0
        if answer in ("", IMPOSSIBLE):
            return 0.0
        ops = _parse_answer(answer, entry)
        if ops is None:
            return 0.0
        gold_ops = _parse_answer(entry.answer, entry)
        if gold_ops is None:
            return 0.0
        if sorted(ops) != sorted(gold_ops):
            return 0.0
        return 1.0


def _parse_answer(answer, entry):
    parts = [p.strip() for p in answer.split(",")]
    ops = []
    for p in parts:
        if not p:
            return None
        if p[0] not in ("M", "D"):
            return None
        opchar = p[0]
        rest = p[1:]
        if ":" not in rest or "r" not in rest or "c" not in rest:
            return None
        head, tail = rest.split(":", 1)
        if not head.isdigit():
            return None
        s = int(head)
        if "r" not in tail:
            return None
        rp, co = tail.split("r", 1)
        colpart = co
        if "c" not in colpart:
            return None
        rowc, cc = colpart.split("c", 1)
        if not rowc.isdigit():
            return None
        row = int(rowc)
        # cc contains column and delta: c{col}+{d} or c{col}-{d}
        if "+" in cc:
            colstr, deltastr = cc.split("+", 1)
            delta = int(deltastr)
        elif "-" in cc:
            colstr, deltastr = cc.split("-", 1)
            delta = -int(deltastr)
        else:
            return None
        if not colstr.isdigit():
            return None
        col = int(colstr) - 1
        row = row - 1
        if opchar == "D" and delta > 0:
            delta = -delta
        if opchar == "M" and delta < 0:
            delta = -delta
        ops.append((s, row, col, delta))
    # validate against table dimensions and ordering
    tables = entry.metadata["tables"]
    nstrata = len(tables)
    nrows = len(tables[0])
    ncols = len(tables[0][0])
    for s, r, c, d in ops:
        if s >= nstrata or r < 0 or r >= nrows or c < 0 or c >= ncols:
            return None
        if d == 0 or abs(d) > entry.metadata["delta_max"]:
            return None
    newt = _apply(tables, ops)
    if not _valid(newt, tables):
        return None
    return ops
