import random
from dataclasses import dataclass
from fractions import Fraction
from math import gcd

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'mean_preserving_spread_order (variant 2 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r5/mean_preserving_spread_order',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 241712510,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _reduce(num, den):
    if num == 0:
        return (0, 1)
    g = gcd(num, den)
    return (num // g, den // g)


def _w1_fraction(outcomes, weights):
    n_ = len(outcomes)
    S = sum(weights)
    num = 0
    cum = 0
    for k in range(1, n_):
        cum += weights[k - 1]
        gap = outcomes[k] - outcomes[k - 1]
        diff = cum * n_ - k * S
        num += abs(diff) * gap
    return _reduce(num, S * n_)


def _mean(outcomes, weights):
    S = sum(weights)
    return Fraction(sum(w * x for w, x in zip(weights, outcomes)), S)


def _parse_frac(s):
    s = str(s).strip()
    if s == "0":
        return (0, 1)
    a, b = s.split("/")
    p, q = int(a), int(b)
    if q <= 0:
        raise ValueError
    return _reduce(p, q)


@dataclass
class MeanPreservingSpreadOrderV2Config(Config):
    count: int = 3
    span: int = 6
    max_weight: int = 4

    def apply_difficulty(self, level):
        self.count = stochastic_rounding(self.count + level)
        self.span = 5 + 4 * level
        self.max_weight = 3 + level


class MeanPreservingSpreadOrder(Task):
    summary = ("Finite weighted outcome distributions with unequal supports and shared means; "
               "compare integrated tails to decide whether mean-preserving redistribution is "
               "possible or identify a violated strike inequality.")
    design_choice = ("Present a single distribution and a target mean; the solver must compute "
                     "the minimal integrated tail difference to a benchmark uniform, returning a "
                     "reduced fraction as the answer.")
    config_cls = MeanPreservingSpreadOrderV2Config
    task_version = 2

    def _choose_instance(self):
        count = self.config.count
        span = self.config.span
        max_w = self.config.max_weight
        for _ in range(400):
            outcomes = sorted(random.sample(range(0, span + 1), count))
            weights = [random.randint(1, max_w) for _ in range(count)]
            if len(set(weights)) == 1:
                continue
            return outcomes, weights
        raise RuntimeError("could not sample non-uniform instance")

    def generate_entry(self):
        outcomes, weights = self._choose_instance()
        p, q = _w1_fraction(outcomes, weights)
        mean = _mean(outcomes, weights)
        check_p, check_q = _w1_fraction(outcomes, weights)
        assert (check_p, check_q) == (p, q)
        assert q > 0
        assert p / q >= 0.0
        return Entry(metadata={
            "outcomes": outcomes,
            "weights": weights,
            "num": p,
            "den": q,
            "mean": str(mean),
        }, answer=f"{p}/{q}")

    def render_prompt(self, metadata):
        outcomes = metadata["outcomes"]
        weights = metadata["weights"]
        n_ = len(outcomes)
        S = sum(weights)
        return (
            f"A finite outcome distribution P assigns positive integer weights {weights} "
            f"respectively to the distinct integer outcomes {outcomes} (weight sum {S}). "
            f"Its mean is {metadata['mean']}. Let U be the uniform benchmark over the same "
            f"{n_} outcomes, giving each outcome probability 1/{n_}. The minimal integrated "
            f"tail difference between P and U is the 1-Wasserstein distance W1(P, U), equal to "
            f"the sum over every adjacent gap of (gap length) times the absolute difference "
            f"between the cumulative probabilities of P and U across that gap. Compute "
            f"W1(P, U). The answer is one reduced fraction in the form p/q."
        )

    def score_answer(self, answer, entry):
        try:
            ap, aq = _parse_frac(answer)
        except (TypeError, ValueError, ZeroDivisionError):
            return 0.0
        ep, eq = int(entry.metadata["num"]), int(entry.metadata["den"])
        ep, eq = _reduce(ep, eq)
        return 1.0 if (ap, aq) == (ep, eq) else 0.0
