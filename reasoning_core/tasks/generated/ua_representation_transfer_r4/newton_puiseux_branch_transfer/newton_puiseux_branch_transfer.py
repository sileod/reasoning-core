import random
from dataclasses import dataclass
from fractions import Fraction
from math import gcd

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class NewtonPuiseuxConfig(Config):
    n_factors: int = 3
    q_max: int = 4
    p_max: int = 8

    def apply_difficulty(self, level):
        self.n_factors = 3 + level
        self.q_max = 3 + level
        self.p_max = 6 + 3 * level


def _build_factors(n_factors, q_max, p_max):
    factors = []
    used = set()
    qs = [random.choice([1] + list(range(2, q_max + 1))) for _ in range(n_factors)]
    for q in qs:
        p = None
        r = None
        for _ in range(512):
            cand = random.randint(1, p_max)
            if q > 1 and gcd(cand, q) != 1:
                continue
            frac = Fraction(cand, q)
            if frac in used:
                continue
            p = cand
            r = frac
            used.add(frac)
            break
        if p is None:
            return None
        factors.append((p, q, r))
    factors.sort(key=lambda t: t[2])
    return factors


def _branch_to_factor(factors, target):
    running = 0
    for idx, (p, q, r) in enumerate(factors):
        running += q
        if target <= running:
            return p, q
    return factors[-1][0], factors[-1][1]


def _poly_string(factors):
    parts = []
    for p, q, r in factors:
        parts.append(f"(y^{q} - x^{p})")
    return "(" + ")(".join(parts) + ")"


class NewtonPuiseuxBranchTransfer(Task):
    summary = ("Factor implicit plane curves into Puiseux branches with distinct fractional "
               "leading exponents and reduced denominators; return the ramification index "
               "(LCD of the fractional exponents) of a chosen branch ordered by increasing "
               "leading exponent.")
    design_choice = ("The instance specifies a polynomial and a branch index; the solver must output "
                     "the ramification index (the least common denominator of the fractional exponents) "
                     "for that branch, with branches ordered by increasing leading exponent.")
    config_cls = NewtonPuiseuxConfig

    def generate_entry(self):
        n_factors = self.config.n_factors
        q_max = self.config.q_max
        p_max = self.config.p_max
        factors = None
        for _ in range(256):
            factors = _build_factors(n_factors, q_max, p_max)
            if factors is not None:
                break
        if factors is None:
            raise RuntimeError("could not build non-degenerate set of factors")

        total_branches = sum(q for _, q, _ in factors)
        target = random.randint(1, total_branches)
        p, q = _branch_to_factor(factors, target)

        if q > 1:
            assert gcd(p, q) == 1, "reduced denominator must equal the ramification index"
        assert q >= 1 and q == int(q)

        factors_json = [[int(p), int(q)] for p, q, _ in factors]
        poly = _poly_string(factors)

        return Entry(
            metadata={
                "factors": factors_json,
                "n_branches": int(total_branches),
                "branch_index": int(target),
                "ramification_index": int(q),
                "polynomial": poly,
            },
            answer=str(int(q)),
        )

    def render_prompt(self, metadata):
        poly = metadata["polynomial"]
        branch_index = metadata["branch_index"]
        n_branches = metadata["n_branches"]
        return (
            f"Consider the plane curve f(x, y) = 0 with f(x, y) = {poly}. "
            f"Its Puiseux branches near the origin are fractional-power series "
            f"y = c*x**e + ... where each factor y^q - x^p contributes q complex branches "
            f"with leading exponent e = p/q. Order all {n_branches} branches by increasing "
            f"leading exponent e. The ramification index of a branch is the least common "
            f"denominator of its fractional exponents in lowest terms. "
            f"What is the ramification index of the {branch_index}-th branch (1-indexed)? "
            f"Answer with the integer."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        stripped = answer.strip()
        if stripped == entry.answer:
            return 1.0
        try:
            if int(stripped) == int(entry.answer):
                return 1.0
        except Exception:
            pass
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'newton_puiseux_branch_transfer (variant 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_transfer_r4/newton_puiseux_branch_transfer',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3020341981,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
