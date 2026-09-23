"""Recompute row/column two-smallest-cost penalties each round, commit the
largest-penalty line to saturating its cheapest cell until exhaustion the
(approximate) transportation assignment via Vogel's Approximation Method (VAM).

The generated instance is a balanced transportation problem: supply per origin,
demand per destination, and a cost matrix. The gold answer is the VAM result:
a semicolon-separated list of 'row:col=amount' entries sorted by row then column
(the allocation map). The total cost and final degenerate cell are derivable
from that map, so the canonical answer here is the allocation map itself.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'penalty_recomputed_transport_assignment (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/penalty_recomputed_transport_assignment',
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


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass
class PenaltyRecomputedConfig(Config):
    n_origins: int = 4
    n_dests: int = 4
    cost_max: int = 20
    total_supply: int = 60

    def apply_difficulty(self, level):
        # difficulty scales the grid size and the supply magnitude -> more lines,
        # more penalty recomputation rounds, longer dependency chains.
        self.n_origins = min(3 + level * 2, 15)
        self.n_dests = min(3 + level * 2, 15)
        self.cost_max = 9 + level * 2
        self.total_supply = 20 + level * 15


# ---------------------------------------------------------------------------
# VAM solver (module-level pure helper, no self access)
# ---------------------------------------------------------------------------
def _vam_allocation(supply, demand, cost):
    """Run Vogel's Approximation Method.

    supply: list of supplies (len m)
    demand: list of demands (len n)
    cost:   m x n cost matrix

    Returns (alloc, total_cost):
      alloc: list of (i, j, amount) allocations
      total_cost: sum of cost[i][j] * amount
    """
    m = len(supply)
    n = len(demand)
    s = list(supply)
    d = list(demand)
    # live rows/cols
    live_rows = list(range(m))
    live_cols = list(range(n))

    alloc = []

    while live_rows and live_cols:
        # compute penalties for each live line: difference between the two
        # smallest costs on that line (over live opposite lines)
        row_pen = []
        for i in live_rows:
            costs = sorted(cost[i][j] for j in live_cols)
            if len(costs) >= 2:
                row_pen.append((costs[1] - costs[0], i))
            else:
                row_pen.append((costs[0], i))
        col_pen = []
        for j in live_cols:
            costs = sorted(cost[i][j] for i in live_rows)
            if len(costs) >= 2:
                col_pen.append((costs[1] - costs[0], j))
            else:
                col_pen.append((costs[0], j))

        # largest penalty among all lines; tie-break by largest index to stay
        # deterministic under sorted iteration (+ column cell cost tie-break)
        best_pen = None
        for pen, i in row_pen:
            if best_pen is None:
                best_pen = ('row', pen, i)
            elif (pen, i) > (best_pen[1], best_pen[2]):
                best_pen = ('row', pen, i)
        for pen, j in col_pen:
            cand = ('col', pen, j)
            if best_pen is None:
                best_pen = cand
            elif (pen, j) > (best_pen[1], best_pen[2]):
                best_pen = cand

        line_type, _pen, idx = best_pen

        if line_type == 'row':
            i = idx
            # cheapest cell on this row among live cols
            j = min(live_cols, key=lambda c: (cost[i][c], -c))
            amt = min(s[i], d[j])
        else:
            j = idx
            i = min(live_rows, key=lambda r: (cost[r][j], -r))
            amt = min(s[i], d[j])

        if amt > 0:
            alloc.append((i, j, amt))
        s[i] -= amt
        d[j] -= amt
        if s[i] == 0:
            live_rows.remove(i)
        if d[j] == 0:
            live_cols.remove(j)

    total_cost = sum(cost[i][j] * amt for (i, j, amt) in alloc)
    return alloc, total_cost


def _format_alloc(alloc):
    """Canonical: semicolon-separated 'row:col=amount' sorted by row then col."""
    sorted_alloc = sorted(alloc, key=lambda t: (t[0], t[1]))
    return ';'.join(f"{i}:{j}={amt}" for (i, j, amt) in sorted_alloc)


def _positive_parts(total, k):
    """Split total into k positive integers summing to total (each >= 1)."""
    if k == 1:
        return [total]
    cuts = sorted(random.sample(range(1, total), k - 1))
    parts = []
    prev = 0
    for c in cuts:
        parts.append(c - prev)
        prev = c
    parts.append(total - prev)
    return parts


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class PenaltyRecomputedTransportAssignment(Task):
    summary = ("Recompute row/column two-smallest-cost penalties each round, "
               "commit the largest-penalty line to saturating its cheapest cell "
               "until exhaustion; answers are the allocation map (canonical "
               "semicolon-separated row:col=amount list sorted by row then col).")
    config_cls = PenaltyRecomputedConfig
    design_choice = ("output the allocation map as a canonical semicolon-separated "
                     "list of 'row:col=amount' entries, sorted by row then column.")

    def generate_entry(self):
        cfg = self.config
        m = cfg.n_origins
        n = cfg.n_dests

        # Bounded generation: supply/demand are balanced by construction.
        while True:
            supply = _positive_parts(cfg.total_supply, m)
            demand = _positive_parts(cfg.total_supply, n)
            if sum(supply) != cfg.total_supply or sum(demand) != cfg.total_supply:
                continue
            if any(x < 1 for x in supply) or any(x < 1 for x in demand):
                continue

            cost = [[random.randint(1, cfg.cost_max) for _ in range(n)]
                    for _ in range(m)]

            alloc, total_cost = _vam_allocation(supply, demand, cost)

            # verify: every unit assigned
            used_s = [0] * m
            used_d = [0] * n
            for (i, j, amt) in alloc:
                used_s[i] += amt
                used_d[j] += amt
            assert used_s == supply, "supply not exhausted"
            assert used_d == demand, "demand not exhausted"

            # deterministic formatting gold
            answer = _format_alloc(alloc)
            break

        return Entry(
            metadata={
                "supply": [int(x) for x in supply],
                "demand": [int(x) for x in demand],
                "cost": [[int(x) for x in row] for row in cost],
                "total_cost": int(total_cost),
                "alloc": [[int(i), int(j), int(a)] for (i, j, a) in alloc],
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        supply = metadata["supply"]
        demand = metadata["demand"]
        cost = metadata["cost"]
        m = len(supply)
        n = len(demand)

        cost_rows = ";\n".join(
            ", ".join(str(cost[i][j]) for j in range(n)) for i in range(m)
        )
        supply_str = ", ".join(str(x) for x in supply)
        demand_str = ", ".join(str(x) for x in demand)

        return (
            "A transportation problem has supply per origin row and demand per "
            "destination column, with a cost matrix where row i, column j is the "
            "per-unit cost. Row supplies: "
            f"[{supply_str}]. Column demands: [{demand_str}]. "
            f"Cost matrix (row, column):\n{cost_rows}\n"
            "Run Vogel's Approximation Method (VAM): at each round compute, for "
            "each remaining line, the penalty as the difference between its two "
            "smallest costs among remaining lines, commit the line with the "
            "largest penalty by saturating its cheapest remaining cell, reduce "
            "supply/demand, and remove exhausted lines; tie-break any equal "
            "penalties by larger line index, then by cheaper cell cost, then by "
            "larger opposite index. Continue until supply and demand are "
            "exhausted.\n"
            "Output the allocation map as a semicolon-separated list of "
            "'row:col=amount' entries sorted by row then column. Example format: "
            "'0:1=5;1:0=3;2:2=7'."
        )

    def score_answer(self, answer, entry):
        # exact-match comparison on the canonical allocation map
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == gold else 0.0
