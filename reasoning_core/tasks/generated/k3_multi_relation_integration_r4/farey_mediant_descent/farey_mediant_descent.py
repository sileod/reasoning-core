import random
from dataclasses import dataclass
from math import gcd

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'farey_mediant_descent (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_multi_relation_integration_r4/farey_mediant_descent',
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


@dataclass
class FareyMediantDescentV1Config(Config):
    denom_max: int = 15

    def apply_difficulty(self, level):
        self.denom_max = 15 + level * level * 8


def _mediant(nl, dl, nr, dr):
    return (nl + nr, dl + dr)


def _path_to_fraction(n, d):
    nl, dl = 0, 1
    nr, dr = 1, 0
    path = []
    while True:
        ml, md = _mediant(nl, dl, nr, dr)
        cmp = n * md - d * ml
        if cmp == 0:
            if (ml, md) != (n, d):
                return None
            return "".join(path)
        if cmp < 0:
            path.append("L")
            nr, dr = ml, md
        else:
            path.append("R")
            nl, dl = ml, md


def _reconstruct(path):
    nl, dl = 0, 1
    nr, dr = 1, 0
    for ch in path:
        ml, md = _mediant(nl, dl, nr, dr)
        if ch == "L":
            nr, dr = ml, md
        else:
            nl, dl = ml, md
    ml, md = _mediant(nl, dl, nr, dr)
    return (ml, md)


def _reduced_pairs(denom_max):
    pairs = []
    for d in range(2, denom_max + 1):
        for n in range(1, d):
            if gcd(n, d) == 1:
                pairs.append((n, d))
    return pairs


class FareyMediantDescent(Task):
    summary = (
        "Search for rationals by mediant descent: keep two Farey neighbors, compare "
        "the target fraction, and move into the half cut by their mediant; answers are "
        "the L/R path to a target fraction reached at its exact reduced numerator/"
        "denominator pair."
    )
    design_choice = (
        "Answer as a canonical L/R string where the descent stops at the exact target "
        "numerator/denominator pair, with ties resolved by always taking the left branch."
    )
    config_cls = FareyMediantDescentV1Config
    task_version = 1

    def generate_entry(self):
        while True:
            n, d = random.choice(_reduced_pairs(self.config.denom_max))
            path = _path_to_fraction(n, d)
            if path is None:
                continue
            if _reconstruct(path) != (n, d):
                continue
            break
        return Entry(
            metadata={"num": n, "den": d, "path": path, "depth": len(path)},
            answer=path,
        )

    def render_prompt(self, metadata):
        n, d = metadata["num"], metadata["den"]
        return (
            f"Consider the reduced fraction {n}/{d}. Run the Stern-Brocot mediant "
            f"descent starting with the Farey neighbors 0/1 and 1/0: at each step take "
            f"the mediant of the two neighbors, write L when {n}/{d} lies strictly "
            f"below that mediant and R when it lies strictly above it, then move into "
            f"the corresponding half (when it equals the mediant, the descent has "
            f"reached {n}/{d} exactly and stops). Give the L/R path to {n}/{d}: a "
            f"string of L and R only, nothing else."
        )

    def score_answer(self, answer, entry):
        return 1.0 if answer == entry.answer else 0.0
