import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _row_key(row):
    return (-sum(row), tuple(-b for b in row))


@dataclass
class OrderingConfig(Config):
    nrow: int = 5
    ncol: int = 5
    density: float = 0.5

    def apply_difficulty(self, level):
        self.nrow = 4 + level
        self.ncol = 4 + level
        self.density = 0.4 + 0.08 * min(level, 5)


class BinaryWeightIncidenceReordering(Task):
    summary = (
        "Treat incidence matrix rows as binary numbers, sort rows by "
        "decreasing weight (ties by decreasing binary value), with columns "
        "fixed in original order, so a single stable pass reveals machine "
        "cells; answers are the final row permutation of original indices, "
        "a block count, or an exceptional-bit count."
    )
    design_choice = (
        "Answer as the final row permutation only, with columns fixed in "
        "original order, to reduce answer space and avoid ambiguity from "
        "column ties."
    )
    config_cls = OrderingConfig

    def generate_entry(self):
        nrow = self.config.nrow
        ncol = self.config.ncol
        density = self.config.density

        matrix = []
        for _ in range(nrow):
            row = [1 if random.random() < density else 0 for _ in range(ncol)]
            matrix.append(row)

        gold_rows = [tuple(r) for r in matrix]
        order = list(range(nrow))
        order.sort(key=lambda i: _row_key(gold_rows[i]))
        perm = list(order)

        return Entry(
            metadata={
                "nrow": nrow,
                "ncol": ncol,
                "matrix": [list(r) for r in matrix],
                "gold": [list(gold_rows[i]) for i in perm],
                "perm": perm,
            },
            answer=str(perm),
        )

    def render_prompt(self, metadata):
        rows = ", ".join("[" + ",".join(str(b) for b in r) + "]" for r in metadata["matrix"])
        nrow = metadata["nrow"]
        return (
            f"We have an incidence matrix with {nrow} rows and "
            f"{metadata['ncol']} columns. Treat each row as a binary number "
            f"whose bits read left to right. Sort the rows by decreasing "
            f"weight (number of 1s), breaking ties by decreasing binary "
            f"value of the row, and keep the columns in their original "
            f"order. This stable single pass reorders the rows into final "
            f"positions as the 'machine cells' of the matrix. "
            f"Give the final row permutation: a bracket-list of length {nrow} "
            f"where position j holds the original (input) row index that now "
            f"sits in final position j. "
            f"Input rows, in original order (indices 0..{nrow-1}): "
            f"[{rows}]. "
            f"Answer in the form [a,b,c,...], e.g. [0,2,1,3]."
        )

    def score_answer(self, answer, entry):
        try:
            s = answer.strip()
            start = s.index("[")
            end = s.index("]")
            parts = [p.strip() for p in s[start + 1 : end].split(",")]
            parsed = [int(p) for p in parts]
        except Exception:
            return 0.0
        nrow = entry.metadata["nrow"]
        if len(parsed) != nrow:
            return 0.0
        if len(set(parsed)) != nrow or any(p < 0 or p >= nrow for p in parsed):
            return 0.0

        matrix = [tuple(r) for r in entry.metadata["matrix"]]
        order = list(range(nrow))
        order.sort(key=lambda i: _row_key(matrix[i]))
        return 1.0 if parsed == order else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'binary_weight_incidence_reordering (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/binary_weight_incidence_reordering',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
