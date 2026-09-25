import random
from dataclasses import dataclass

import numpy as np
from scipy.spatial import ConvexHull

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'support_function_composition (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_representation_r4/support_function_composition',
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


@dataclass
class SupportFunctionCompositionConfig(Config):
    n: int = 5
    coord_bound: int = 20
    depth: int = 3

    def apply_difficulty(self, level):
        self.n = stochastic_rounding(5 + 2 * level)
        self.depth = stochastic_rounding(3 + level)
        self.coord_bound = stochastic_rounding(20 + 4 * level)


def _point_set(rng_mult, n, bound):
    pts = set()
    tries = 0
    while len(pts) < n and tries < 40:
        p = (random.randint(-bound, bound), random.randint(-bound, bound))
        pts.add(p)
        tries += 1
    return sorted(pts)


class SupportFunctionComposition(Task):
    summary = "Evaluate directional extrema of shapes built from point sets and boxes using convex hulls, Minkowski sums, translations, and linear maps; answer support values without expanding the shape."
    design_choice = "Each instance provides a fixed direction vector and asks for the support function value of the Minkowski sum of two convex hulls, requiring the sum of individual support values from the original point sets."
    config_cls = SupportFunctionCompositionConfig

    def generate_entry(self):
        cfg = self.config
        n = max(cfg.n, 6)
        bound = cfg.coord_bound
        P = _point_set(None, n, bound)
        Q = _point_set(None, n, bound)
        while len(P) < 3 or len(Q) < 3:
            P = _point_set(None, n, bound)
            Q = _point_set(None, n, bound)

        d = (random.randint(-1, 1), random.randint(1, 4))
        if d[0] == 0 and d[1] == 0:
            d = (1, 1)

        support_p = max(p[0] * d[0] + p[1] * d[1] for p in P)
        support_q = max(q[0] * d[0] + q[1] * d[1] for q in Q)
        support_sum = support_p + support_q

        return Entry(
            metadata={
                "P": P,
                "Q": Q,
                "direction": d,
                "support_P": support_p,
                "support_Q": support_q,
            },
            answer=str(support_sum),
        )

    def render_prompt(self, metadata):
        P = metadata["P"]
        Q = metadata["Q"]
        d = metadata["direction"]
        return (
            f"A convex shape is the Minkowski sum of the convex hulls of the point "
            f"sets P={P} and Q={Q} (Minkowski sum is the set of all p+q with p in the "
            f"first hull and q in the second). The support function value in direction "
            f"d=({d[0]}, {d[1]}) of a shape S equals max over S of the dot product "
            f"with d. The support function of a Minkowski sum is the sum of the "
            f"individual support functions. What is the support value of the Minkowski "
            f"sum of the two hulls in direction d=({d[0]}, {d[1]})? Answer with one integer."
        )


def _score(answer):
    try:
        return int(float(str(answer).strip()))
    except (ValueError, TypeError):
        return None


def score_answer(answer, entry):
    val = _score(answer)
    if val is None:
        return 0.0
    return 1.0 if val == int(entry.answer) else 0.0
