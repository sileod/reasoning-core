"""Rational observables tested under shared translations, Galilean boosts, and coordinate rescalings."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class InvariantConfig(Config):
    level: int = 0
    coeff_range: int = 3

    def apply_difficulty(self, level):
        self.level = level
        self.coeff_range = 3 + 2 * level


def _param_dep(kind, coeffs, t, x, y):
    """Coefficient of the transform parameter in the transformed observable value."""
    a, b, c = coeffs
    if kind == "translation":
        return a + b
    if kind == "boost":
        return (a + b) * t
    return a * x + b * y


def _sample_coeffs(kind, want_inv, R, t, x, y):
    bool_test = None
    while True:
        a = random.randrange(-R, R + 1)
        b = random.randrange(-R, R + 1)
        c = random.randrange(-R, R + 1)
        sat = _param_dep(kind, (a, b, c), t, x, y) == 0
        if sat == want_inv:
            return a, b, c


class FrameIndependentObservables(Task):
    summary = ("Test rational observables under shared translations, Galilean boosts, and "
               "coordinate rescalings; identify expressions unchanged for every frame "
               "parameter or recover coefficients required for invariance.")
    config_cls = InvariantConfig

    def generate_entry(self):
        level = self.config.level
        R = self.config.coeff_range
        kind = random.choice(["translation", "boost", "rescale"])
        want_inv = random.random() < 0.5

        t = random.randrange(1, 4 + level)
        x = random.randrange(-5, 6)
        y = random.randrange(-5, 6)

        a, b, c = _sample_coeffs(kind, want_inv, R, t, x, y)
        coeffs = (a, b, c)
        answer = "yes" if want_inv else "no"

        params = [-3, -1, 1, 3]
        vals = [_expr_value(kind, coeffs, t, x, y, p) for p in params]
        actual_inv = len(set(vals)) == 1
        assert actual_inv == want_inv, (kind, coeffs, t, x, y, vals)

        return Entry(metadata={
            "kind": kind,
            "coeffs": list(coeffs),
            "t": int(t), "x": int(x), "y": int(y),
            "level": int(level),
            "probe_params": params,
            "probe_vals": [int(v) for v in vals],
        }, answer=answer)

    def _build_prompt(self, kind, coeffs, t, x, y):
        a, b, c = coeffs
        kind_desc = {
            "translation": ("translation", "we add the same constant to both spatial coordinates"),
            "boost": ("Galilean boost", "we give both spatial coordinates a shared constant velocity"),
            "rescale": ("spatial rescaling", "we multiply both spatial coordinates by a common factor"),
        }
        kname, kdesc = kind_desc[kind]
        return (
            f"Consider the observable O = {a}*x + {b}*y + {c}*t evaluated at t={t}, "
            f"x={x}, y={y}, where x and y are spatial coordinates and t is time. "
            f"Under a {kname} of the frame in which {kdesc}, can the value of O change? "
            f"Answer yes if O is unchanged for every possible {kname} parameter, no if "
            f"some parameter changes it. Answer with a single word."
        )

    def render_prompt(self, metadata):
        return self._build_prompt(metadata["kind"], tuple(metadata["coeffs"]),
                                  metadata["t"], metadata["x"], metadata["y"])

    def score_answer(self, answer, entry):
        a = str(answer).strip().lower()
        gold = entry.answer
        if a in ("yes", "no"):
            return 1.0 if a == gold else 0.0
        return 0.0


def _expr_value(kind, coeffs, t, x, y, param):
    a, b, c = coeffs
    if kind == "translation":
        return a * x + b * y + c * t + (a + b) * param
    if kind == "boost":
        return a * (x - param * t) + b * (y - param * t) + c * t
    return a * param * x + b * param * y + c * t


TASK_META = {'parent_source_id': None,
 'idea': 'frame_independent_observables (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_invariants_r4/frame_independent_observables',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1034322864,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
