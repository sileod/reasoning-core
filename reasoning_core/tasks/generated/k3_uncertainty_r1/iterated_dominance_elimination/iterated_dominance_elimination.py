import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task


@dataclass
class IteratedDominanceEliminationConfig(Config):
    rows: int = 3
    cols: int = 3
    payoff_low: int = 1
    payoff_high: int = 6
    max_removals: int = 4

    def apply_difficulty(self, level):
        self.payoff_low = 1
        self.payoff_high = 6 + level * 4
        self.rows = 2 + (level // 2)
        self.cols = 2 + (level // 2)
        self.max_removals = 1 + level // 2


def _strictly_dominates(u, v):
    ge = all(a >= b for a, b in zip(u, v))
    gt = any(a > b for a, b in zip(u, v))
    return ge and gt


def _reduce_brute(payoffs, rows, cols):
    row_mats = [payoffs[0], payoffs[1]]
    active_rows = list(range(rows))
    active_cols = list(range(cols))
    removed = 0
    while True:
        progressed = False
        for i in active_rows:
            for j in active_rows:
                if i == j:
                    continue
                row_i = [row_mats[0][i][c] for c in active_cols]
                row_j = [row_mats[0][j][c] for c in active_cols]
                if _strictly_dominates(row_i, row_j):
                    active_rows.remove(j)
                    removed += 1
                    progressed = True
                    break
            if progressed:
                break
        if progressed:
            continue
        for a in active_cols:
            for b in active_cols:
                if a == b:
                    continue
                col_a = [row_mats[1][r][a] for r in active_rows]
                col_b = [row_mats[1][r][b] for r in active_rows]
                if _strictly_dominates(col_a, col_b):
                    active_cols.remove(b)
                    removed += 1
                    progressed = True
                    break
            if progressed:
                break
        if not progressed:
            break
    active_rows.sort()
    active_cols.sort()
    return active_rows, active_cols, removed


class IteratedDominanceElimination(Task):
    summary = ("Reduce two-player bimatrix games by repeated deletion of strictly "
               "dominated pure strategies on either side, re-scanning after each removal "
               "since new dominances emerge, until a fixpoint; answer both players' "
               "surviving strategy sets.")
    design_choice = ("Generate games where dominance chains are long and interleaved, "
                     "requiring multiple re-scans across both players to reach the "
                     "fixpoint, with answer sets of varying sizes.")
    config_cls = IteratedDominanceEliminationConfig

    def generate_entry(self):
        cfg = self.config
        rows, cols = cfg.rows, cfg.cols
        low, high = cfg.payoff_low, cfg.payoff_high

        for _ in range(400):
            row_pay = [[random.randint(low, high) for _ in range(cols)]
                       for _ in range(rows)]
            cold_pay = [[random.randint(low, high) for _ in range(cols)]
                        for _ in range(rows)]
            _, _, removed = _reduce_brute((row_pay, cold_pay), rows, cols)
            if removed >= cfg.max_removals:
                break
        else:
            raise RuntimeError("could not reach target removals")

        active_rows, active_cols, removed = _reduce_brute(
            (row_pay, cold_pay), rows, cols)

        assert 0 <= removed <= rows + cols
        assert len(active_rows) >= 1 and len(active_cols) >= 1

        answer = (tuple(active_rows), tuple(active_cols))
        metadata = {
            "rows": rows,
            "cols": cols,
            "row_payoffs": [r[:] for r in row_pay],
            "column_payoffs": [r[:] for r in cold_pay],
            "surviving_rows": list(active_rows),
            "surviving_cols": list(active_cols),
            "removed_count": removed,
        }
        return Entry(metadata=metadata, answer=repr(answer))

    def render_prompt(self, metadata):
        m = metadata
        row_lines = []
        for r in range(m["rows"]):
            entries = [f"({m['row_payoffs'][r][c]},{m['column_payoffs'][r][c]})"
                       for c in range(m["cols"])]
            row_lines.append("[" + ", ".join(entries) + "]")
        grid = "\n".join(f"  {rl}" for rl in row_lines)
        return (
            f"Below is the bimatrix of a two-player game. Row player chooses a row "
            f"(rows 0..{m['rows']-1}); column player chooses a column (cols 0.."
            f"{m['cols']-1}); each entry is (row payoff, column payoff). Repeatedly "
            f"delete every pure strategy that is strictly dominated by another pure "
            f"strategy of the same player (a strategy dominates another when its payoff "
            f"is never worse and strictly better in at least one entry). After each "
            f"deletion re-scan both players because new dominances can emerge. Continue "
            f"until no further deletion is possible.\n"
            f"Report the surviving strategy sets as two sorted tuples "
            f"(surviving_rows, surviving_cols), e.g. ((0, 2), (1,)).\n"
            f"Game:\n{grid}"
        )

    def score_answer(self, answer, entry):
        m = entry.metadata
        canonical = ((tuple(m["surviving_rows"]),
                      tuple(m["surviving_cols"])))
        try:
            parsed = eval(answer)
            return 1.0 if parsed == canonical else 0.0
        except Exception:
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'iterated_dominance_elimination (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_uncertainty_r1/iterated_dominance_elimination',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
