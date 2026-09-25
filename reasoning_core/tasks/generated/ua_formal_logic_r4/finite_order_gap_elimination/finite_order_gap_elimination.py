import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class FiniteOrderGapEliminationConfig(Config):
    nvars: int = 3
    max_value: int = 6

    def apply_difficulty(self, level):
        self.nvars = 4 + level
        self.max_value = 12 + level


def _eliminate(metadata):
    n = metadata["n"]
    names = metadata["names"]
    split = metadata["split"]
    a = metadata["a"]
    b = metadata["b"]
    parts = []
    for j in range(n - 1):
        if j == split:
            parts.append(f"{names[j + 1]} - {names[j]} = {a + b}")
        else:
            parts.append(f"{names[j]} < {names[j + 1]}")
    return " & ".join(parts)


class FiniteOrderGapElimination(Task):
    summary = "Eliminate quantified variables from formulas over finite linear orders by reasoning about endpoint and inter-variable gaps; return an equivalent condition on the free variables' order and gap sizes."
    design_choice = "Answer as a canonical conjunction/disjunction of atomic gap constraints, e.g., 'x1 < x2 & x2 - x1 = 1 & x3 - x2 > 0'"
    config_cls = FiniteOrderGapEliminationConfig

    def generate_entry(self):
        n = self.config.nvars
        a = random.randint(1, self.config.max_value)
        b = random.randint(1, self.config.max_value)
        split = random.randrange(n - 1)
        names = ["x%d" % i for i in range(n)]
        metadata = {
            "n": n,
            "names": names,
            "split": split,
            "a": a,
            "b": b,
            "free_vars": names,
        }
        return Entry(metadata=metadata, answer=_eliminate(metadata))

    def render_prompt(self, metadata):
        n = metadata["n"]
        names = metadata["names"]
        split = metadata["split"]
        a = metadata["a"]
        b = metadata["b"]
        lo = f"{names[split]}"
        hi = f"{names[split + 1]}"
        chain = " < ".join(names)
        return (
            f"Over a finite linear order, consider ordered free variables {chain}. "
            f"Eliminate the quantified variable y from the statement "
            f"'there exists y such that y - {lo} = {a} and {hi} - y = {b}', "
            f"where y lies strictly between {lo} and {hi}. "
            f"Give an equivalent condition on the free variables as a conjunction of atomic gap constraints "
            f"using only '<' between a pair and exact gaps 'u - v = k' "
            f"(e.g. 'x0 < x1 & x2 - x1 = 5 & x2 < x3')."
        )


def score_answer(answer, entry):
    return 1.0 if answer == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'finite_order_gap_elimination (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/finite_order_gap_elimination',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
