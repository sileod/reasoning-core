import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _invariant_factors(matrix):
    from sympy import Matrix
    from sympy.matrices.normalforms import smith_normal_form
    smf = smith_normal_form(Matrix(matrix))
    rows, cols = smf.shape
    factors = [int(smf[i, i]) for i in range(min(rows, cols))]
    nonzero = [f for f in factors if f != 0]
    inv = tuple(sorted(nonzero))
    for d1, d2 in zip(inv, inv[1:]):
        if d2 % d1 != 0:
            raise RuntimeError(f"invariant factors not divisibility-ordered: {inv}")
    return inv


@dataclass
class SNFConfig(Config):
    rows: int = 2
    cols: int = 2
    magnitude: int = 9

    def apply_difficulty(self, level):
        import random as _r
        if level <= 1:
            self.rows, self.cols = 2, 2
        elif level <= 3:
            self.rows = _r.choice([2, 3])
            self.cols = _r.choice([2, 3])
        else:
            self.rows = _r.choice([3, 4])
            self.cols = _r.choice([3, 4])
        self.magnitude = 9


class SmithNormalForm(Task):
    summary = ("Reduce small integer matrices by exact row and column "
               "operations to diagonal Smith normal form, returning the "
               "invariant factors as the sorted diagonal tuple.")
    design_choice = ("Vary matrix size from 2x2 to 4x4, with entries in "
                     "[-9,9], and require the sorted diagonal tuple of "
                     "invariant factors as answer.")
    config_cls = SNFConfig

    def generate_entry(self):
        rows = self.config.rows
        cols = self.config.cols
        base_lim = 3
        for _ in range(2000):
            base = [[random.randint(-base_lim, base_lim)
                     for _ in range(cols)] for _ in range(rows)]
            r = random.randint(1, 3)
            matrix = [[c * r for c in row] for row in base]
            inv = _invariant_factors(matrix)
            for f in inv:
                if f < 0:
                    raise RuntimeError("negative invariant factor")
            return Entry(metadata={"matrix": matrix, "rows": rows,
                                   "cols": cols},
                         answer=str(inv))
        raise RuntimeError("failed to generate SNF instance")

    def render_prompt(self, metadata):
        rows = len(metadata["matrix"])
        cols = len(metadata["matrix"][0])
        return (
            f"Compute the Smith normal form of the following {rows}x{cols} "
            f"integer matrix using exact integer row and column operations, "
            f"and give its nonzero invariant factors.\n\n"
            f"Matrix:\n{metadata['matrix']}\n\n"
            f"Answer as the sorted tuple of the positive diagonal entries "
            f"d1 | d2 | ... | dk, for example (1, 2, 4). If the matrix reduces "
            f"to all zeros, answer ()."
        )

    def score_answer(self, answer, entry):
        gold = entry.answer
        try:
            a = _parse_tuple(answer)
            g = _parse_tuple(gold)
        except Exception:
            return 0.0
        return 1.0 if a == g else 0.0


def _parse_tuple(text):
    text = text.strip()
    if text == "()":
        return ()
    if not (text.startswith("(") and text.endswith(")")):
        raise ValueError("not a tuple")
    return tuple(int(p) for p in text[1:-1].split(",") if p.strip())


TASK_META = {'parent_source_id': None,
 'idea': 'smith_normal_form (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_rule_induction_r1/smith_normal_form',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
