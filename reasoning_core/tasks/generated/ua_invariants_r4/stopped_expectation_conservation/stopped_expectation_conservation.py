"""Harmonic-observable expectation conservation through bounded stopping.

A finite Markov chain on a path {0,1,...,n+1} with absorbing ends 0 and n+1 and
transient interior states. An observable h is harmonic on every transient state
(h(i) = expected h at the next state), with boundary values h(0)=a, h(n+1)=b.
The process is stopped at tau = min(first hit of {0,n+1}, K). Because h is a
martingale along the stay/step walk and tau is a bounded stopping time,
E[h(X_tau)] = h(s) exactly. The answer is h(s), computed by solving the harmonic
extension at the start state. Optionally a stay probability r adds surface variety
without changing the harmonic values (h stays the unique linear interpolation).
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'stopped_expectation_conservation (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_invariants_r4/stopped_expectation_conservation',
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
class StoppedExpectationConfig(Config):
    n: int = 2
    maxabs: int = 2

    def apply_difficulty(self, level):
        self.n = 2 + level
        self.maxabs = 2 + 2 * level


def _harmonic_start(n, s, a, b):
    """Harmonic value at interior start s on the path 0..n+1 with boundary (a,b)."""
    total = Fraction(a) * Fraction(n + 1 - s) + Fraction(b) * Fraction(s)
    return total / Fraction(n + 1)


def _parse_frac(text):
    """Parse an answer that is a reduced fraction p/q or an integer."""
    if text is None:
        return None
    text = str(text).strip()
    if "/" in text:
        try:
            num, den = text.split("/", 1)
            return Fraction(int(num), int(den))
        except Exception:
            return None
    try:
        return Fraction(int(text))
    except Exception:
        return None


class StoppedExpectationConservation(Task):
    summary = ("Infer terminal expectations and absorption values under bounded "
               "stopping of finite Markov chains using harmonic observables; "
               "unique rational terminal expectations via harmonic extension.")
    design_choice = ("Instances present a finite Markov chain with a bounded stopping rule "
                     "(e.g., stop after K steps or on hitting a set); the answer is the unique "
                     "terminal expectation of a given harmonic observable, expressed as a fraction.")
    config_cls = StoppedExpectationConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n
        maxabs = max(1, self.config.maxabs)
        while True:
            a = random.randint(-maxabs, maxabs)
            b = random.randint(-maxabs, maxabs)
            if a == b:
                continue
            s = random.randint(1, n)
            stay = random.choice([0, Fraction(1, 4), Fraction(1, 2)])
            if stay == 0:
                plo = ph = Fraction(1, 2)
            else:
                step = (Fraction(1) - stay) / 2
                plo = ph = step
            K = max(1, n)
            lo, hi = (a, b) if a < b else (b, a)
            h_s = _harmonic_start(n, s, a, b)
            dom_ok = lo <= h_s <= hi
            if not dom_ok:
                continue
            metadata = {
                "n": n,
                "start": s,
                "boundary": {"lo": a, "hi": b},
                "stay": str(stay),
                "p_left": str(plo),
                "p_right": str(ph),
                "K": K,
                "absorbing": [0, n + 1],
                "a": a,
                "b": b,
            }
            answer = (f"{h_s.numerator}/{h_s.denominator}"
                      if h_s.denominator != 1 else str(h_s.numerator))
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["n"]
        a = metadata["a"]
        b = metadata["b"]
        s = metadata["start"]
        stay = metadata["stay"]
        pc = metadata["p_left"]
        K = metadata["K"]
        if stay == "0":
            motion = (
                f"from transient state i it moves to i-1 with probability {pc} and to "
                f"i+1 with probability {pc}"
            )
        else:
            motion = (
                f"from transient state i it stays put with probability {stay}, moves to "
                f"i-1 with probability {pc} and to i+1 with probability {pc}"
            )
        return (
            f"Consider a finite Markov chain on the integer states 0,1,...,{n + 1}. "
            f"The states 0 and {n + 1} are absorbing; the states 1..{n} are transient. "
            f"A particle starts at state {s}. At each step, {motion}. "
            f"Define an observable h that is harmonic on every transient state: for each "
            f"transient i, h(i) equals the expectation of h at the next state reached from i. "
            f"The boundary values are h(0) = {a} and h({n + 1}) = {b}. "
            f"The process is stopped at tau = min(first time the particle hits "
            f"{{0, {n + 1}}}, {K}), i.e. after at most {K} steps or on hitting an absorbing "
            f"state, whichever is first. By harmonicity h forms a martingale, so the expected "
            f"terminal value E[h(X_tau)] equals the harmonic value h({s}) at the start "
            f"state, which is uniquely determined by the boundary values and the transition "
            f"structure. Compute h({s}).\n"
            f"Give the answer as a reduced fraction p/q or an integer, with no other text."
        )

    def score_answer(self, answer, entry):
        gold = _parse_frac(entry.answer)
        got = _parse_frac(answer)
        if gold is None or got is None:
            return 0.0
        return 1.0 if got == gold else 0.0
