import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'gf2_matrix_rank (draw 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/gf2_matrix_rank',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _pivot_columns(matrix):
    rows = [int(''.join(str(c) for c in r), 2) for r in matrix]
    ncols = len(matrix[0])
    pivots = []
    for col in range(ncols):
        bit = 1 << (ncols - 1 - col)
        piv = None
        for i in range(len(pivots), len(rows)):
            if rows[i] & bit:
                piv = i
                break
        if piv is None:
            continue
        rows[len(pivots)], rows[piv] = rows[piv], rows[len(pivots)]
        for i in range(len(rows)):
            if i != len(pivots) and (rows[i] & bit):
                rows[i] ^= rows[len(pivots)]
        pivots.append(col)
    return pivots


def _rank(matrix):
    return len(_pivot_columns(matrix))


@dataclass
class GF2MatrixRankConfig(Config):
    min_rows: int = 3
    max_rows: int = 5
    min_cols: int = 3
    max_cols: int = 5

    def apply_difficulty(self, level):
        d = 3 + level
        self.min_rows = d
        self.max_rows = d + 2
        self.min_cols = d
        self.max_cols = d + 2


class GF2MatrixRank(Task):
    summary = "Row-reduce a binary matrix over GF(2), reporting the pivot column set as a sorted comma-separated list of indices, across square, tall, and wide shapes with varied density and differing ranks."
    design_choice = "Report the pivot column set as a sorted comma-separated list of indices (e.g., '0,2,5'), with rank implied; ensure different ranks occur by controlling density."
    config_cls = GF2MatrixRankConfig

    def generate_entry(self):
        cfg = self.config
        nrows = random.randint(cfg.min_rows, cfg.max_rows)
        ncols = random.randint(cfg.min_cols, cfg.max_cols)

        r = random.randint(1, min(nrows, ncols))
        density = random.choice([0.3, 0.5, 0.7])

        core = []
        for i in range(r):
            row = [0] * ncols
            row[i] = 1
            for j in range(r, ncols):
                if random.random() < density:
                    row[j] = 1
            core.append(row)

        rows = list(core)
        for _ in range(nrows - r):
            combo = [0] * ncols
            for core_row in core:
                if random.random() < 0.5:
                    for j in range(ncols):
                        combo[j] ^= core_row[j]
            rows.append(combo)

        perm = list(range(ncols))
        random.shuffle(perm)
        matrix = [[row[perm[j]] for j in range(ncols)] for row in rows]

        rank = _rank(matrix)
        assert rank == r, (rank, r)

        pivots = _pivot_columns(matrix)
        assert len(pivots) == r
        assert pivots == sorted(pivots) and all(pivots[i] < pivots[i + 1] for i in range(len(pivots) - 1))
        answer = ','.join(str(c) for c in pivots)

        return Entry(metadata={
            "matrix": matrix,
            "rank": rank,
            "density": density,
        }, answer=answer)

    def render_prompt(self, metadata):
        rows = '\n'.join(' '.join(str(c) for c in row) for row in metadata['matrix'])
        return (
            f"Consider the following binary matrix over GF(2):\n{rows}\n"
            "Row-reduce it with Gaussian elimination. Report the pivot column set as a "
            "sorted comma-separated list of column indices, 0-based, e.g. '0,2,5'."
        )


def _parse_indices(answer):
    return [int(x) for x in answer.split(',') if x.strip() != '']


def score_answer(answer, entry):
    try:
        got = _parse_indices(answer)
    except (TypeError, ValueError):
        return 0.0
    expected = [int(x) for x in entry.answer.split(',')]
    try:
        return 1.0 if got == expected else 0.0
    except Exception:
        return 0.0
