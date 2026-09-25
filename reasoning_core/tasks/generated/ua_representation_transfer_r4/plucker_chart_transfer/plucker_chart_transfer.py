import random
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

import sympy as sp

from reasoning_core.template import Config, Entry, Task


def _labels(dim, ambient):
    return list(combinations(range(ambient), dim))


def _plucker_coords(matrix, dim, labels):
    M = sp.Matrix(matrix)
    return [int(M[:, cols].det()) for cols in labels]


def _spanning_matrix(dim, ambient, rng):
    while True:
        rows = [[rng.randint(-6, 6) for _ in range(ambient)] for _ in range(dim)]
        if sp.Matrix(rows).rank() == dim:
            return [[int(x) for x in row] for row in sp.Matrix(rows).tolist()]


def _reduce(num, den):
    f = Fraction(num, den)
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


TASK_META = {'parent_source_id': None,
 'idea': 'plucker_chart_transfer (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_transfer_r4/plucker_chart_transfer',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class PluckerChartTransferConfig(Config):
    range_val = 6

    def apply_difficulty(self, level):
        pass


class PluckerChartTransfer(Task):
    summary = ("Translate subspaces among spanning matrices, normalized Plucker coordinates "
               "and affine Grassmann charts with changing pivot sets; recover a chart entry or "
               "minor ratio, or detect an unavailable chart.")
    design_choice = ("return a single integer minor ratio as a reduced fraction string, with "
                     "pivot-set changes forcing recomputation of ratios from scratch.")
    config_cls = PluckerChartTransferConfig
    task_version = 2

    def _params(self, level):
        if level <= 1:
            return 2, 4
        if level <= 3:
            return 2, 5
        if level == 4:
            return 3, 5
        return 3, 6

    def generate_entry(self):
        dim, ambient = self._params(self.config.level)
        labels = _labels(dim, ambient)
        while True:
            matrix = _spanning_matrix(dim, ambient, random)
            coords = _plucker_coords(matrix, dim, labels)
            nonz = [i for i, c in enumerate(coords) if c != 0]
            if len(nonz) < 2:
                continue
            base_i = random.choice(nonz)
            others = [i for i in nonz if i != base_i]
            target_i = random.choice(others)
            num = coords[target_i]
            den = coords[base_i]
            assert den != 0 and num != 0
            answer = _reduce(num, den)
            return Entry(
                metadata={
                    "dim": dim,
                    "ambient": ambient,
                    "matrix": matrix,
                    "base_pivot": list(labels[base_i]),
                    "target_pivot": list(labels[target_i]),
                    "labels": [list(c) for c in labels],
                    "coords": coords,
                    "answer": answer,
                },
                answer=answer,
            )

    def render_prompt(self, metadata):
        dim = metadata["dim"]
        ambient = metadata["ambient"]
        matrix = metadata["matrix"]
        base = metadata["base_pivot"]
        target = metadata["target_pivot"]
        rows = "; ".join(",".join(str(x) for x in r) for r in matrix)
        base_cols = ",".join(str(c) for c in base)
        target_cols = ",".join(str(c) for c in target)
        return (
            f"Fix k={dim} and n={ambient}. The Grassmannian Gr(k, n) parametrizes "
            f"{dim}-dimensional linear subspaces of R^{ambient}. The {dim}-plane V is realized as "
            f"the row span of the spanning matrix M = [{rows}], whose Plucker coordinates are the "
            f"size-{dim} minors of M on each size-{dim} column set. "
            f"Change chart: transfer from the pivot set P = ({base_cols}) to the pivot set "
            f"Q = ({target_cols}). Give the ratio of the new (Q) Plucker coordinate to the old "
            f"(P) Plucker coordinate, computed from scratch in the new chart. "
            f"Answer as a single reduced fraction, e.g. -2/3 or 5."
        )

    def score_answer(self, answer, entry):
        given = (answer or "").strip()
        gold = entry.answer
        if given == gold:
            return 1.0
        try:
            if Fraction(given) == Fraction(gold):
                return 1.0
        except Exception:
            pass
        return 0.0
