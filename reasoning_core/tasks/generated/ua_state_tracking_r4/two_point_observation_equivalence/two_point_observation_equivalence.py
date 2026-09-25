import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'two_point_observation_equivalence (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/two_point_observation_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class TwoPointObservationEquivalenceConfig(Config):
    rows: int = 2
    cols: int = 2
    modulus: int = 5

    def apply_difficulty(self, level):
        self.rows = 3 + (level // 2)
        self.cols = 3 + (level // 2)
        self.modulus = 5 + level


def _correlations(rows, cols, modulus, values):
    n = rows * cols
    seen = {}
    for dr in range(rows):
        for dc in range(cols):
            if dr == 0 and dc == 0:
                continue
            c = 0
            for g in range(n):
                gr, gc = divmod(g, cols)
                h = ((gr + dr) % rows) * cols + ((gc + dc) % cols)
                c += values[g] * values[h]
            key = (dr, dc)
            seen[key] = c
    return seen


def _is_flat(rows, cols, modulus, values):
    corrs = _correlations(rows, cols, modulus, values)
    vals = set(corrs.values())
    return len(vals) == 1


class TwoPointObservationEquivalence(Task):
    summary = ("Weighted patterns on cyclic grids Z_r x Z_c; decide whether all weighted "
               "two-point displacement correlations (autocorrelations) are equal under "
               "every translation, with balanced yes/no answers and varied weight patterns.")
    design_choice = "Answer as a yes/no on whether all weighted two-point displacement correlations are equal under every translation and reflection, with instances balanced across both outcomes."
    config_cls = TwoPointObservationEquivalenceConfig

    def generate_entry(self):
        cfg = self.config
        rows, cols, modulus = cfg.rows, cfg.cols, cfg.modulus
        n = rows * cols

        is_flat = None
        for _ in range(40):
            target = random.random() < 0.5
            if target:
                style = random.random() < 0.5
                if style:
                    value = random.randrange(1, modulus + 1)
                    values = [value] * n
                else:
                    value = random.randrange(1, modulus)
                    values = [0] * n
                    values[random.randrange(n)] = value
                is_flat = _is_flat(rows, cols, modulus, values)
                if is_flat:
                    break
            else:
                values = [random.randrange(modulus) for _ in range(n)]
                if not _is_flat(rows, cols, modulus, values):
                    break
        else:
            raise RuntimeError("could not construct a valid instance")

        answer = "yes" if is_flat else "no"
        return Entry(metadata={
            "rows": rows, "cols": cols, "modulus": modulus, "values": values,
        }, answer=answer)

    def render_prompt(self, metadata):
        rows = metadata["rows"]
        cols = metadata["cols"]
        values = metadata["values"]
        m = metadata["modulus"]
        lines = []
        for r in range(rows):
            row = " ".join(str(values[r * cols + c]) for c in range(cols))
            lines.append(row)
        grid = "\n".join(lines)
        return (
            f"We place weights on the cells of a cyclic (toroidal) grid of {rows} rows and "
            f"{cols} columns, each entry an integer in [0,{m}). The two-point displacement "
            f"correlation of a displacement (dr,dc) is the sum over all cells g of w(g)*w(g+(dr,dc)), "
            f"indices wrapping around. Treat (dr,dc) and (-dr,-dc) as the same displacement.\n"
            f"Grid weights:\n{grid}\n\n"
            f"Are all these two-point displacement correlations equal, i.e. do they take one "
            f"common value for every nonzero displacement, unchanged under every translation "
            f"and reflection of the grid? State your verdict in one word, either the affirmative "
            f"or the negative, and nothing else."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        gold = _is_flat(entry.metadata["rows"], entry.metadata["cols"],
                        entry.metadata["modulus"], entry.metadata["values"])
        expected = "yes" if gold else "no"
        if isinstance(answer, str):
            a = answer.strip().lower()
            if a == expected:
                return 1.0
            if a in ("yes", "no"):
                return 0.0
            return 0.0
        return 0.0
