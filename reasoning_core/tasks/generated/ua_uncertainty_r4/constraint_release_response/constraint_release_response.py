import random
from dataclasses import dataclass

import sympy as sp

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _equilibrium(loads, pinned):
    n = len(loads)
    pinned_set = set(pinned)
    free = [i for i in range(n) if i not in pinned_set]

    def add_spring(i, j, K):
        K[i][i] += 1
        K[j][j] += 1
        K[i][j] -= 1
        K[j][i] -= 1

    K = [[0] * n for _ in range(n)]
    K[0][0] += 1  # spring to left fixed wall
    for i in range(n - 1):
        add_spring(i, i + 1, K)
    K[n - 1][n - 1] += 1  # spring to right fixed wall

    A = sp.zeros(len(free), len(free))
    b = sp.zeros(len(free), 1)
    for r, i in enumerate(free):
        for c, j in enumerate(free):
            A[r, c] = sp.Rational(K[i][j])
        b[r] = sp.Rational(loads[i])
    u_free = A.LUsolve(b)
    values = [sp.Integer(0)] * n
    for k, i in enumerate(free):
        values[i] = u_free[k]
    return values


def _fmt(r):
    if r == 0:
        return "0"
    num = sp.numer(r)
    den = sp.denom(r)
    sign = "-" if num < 0 else ""
    a, b = abs(int(num)), int(den)
    if b == 1:
        return f"{sign}{a}"
    return f"{sign}{a}/{b}"


def _spaced(values):
    return ", ".join(_fmt(v) for v in values)


@dataclass
class ConstraintReleaseConfig(Config):
    n_min: int = 4
    n_max: int = 4
    max_pins: int = 1
    max_load: int = 2

    def apply_difficulty(self, level):
        self.n_min = 3 + level
        self.n_max = 4 + level
        self.max_pins = 1 + level
        self.max_load = 2 + level


class ConstraintReleaseResponse(Task):
    summary = ("Release a redundant support pin in a spring-mass chain with stated "
               "loads, enforce the remaining constraints, recompute the "
               "minimum-energy equilibrium, and return the released mass's "
               "displacement change as a signed fraction.")
    design_choice = ("Each instance gives a single redundant constraint to release; "
                     "the answer is the change in a specified displacement component, "
                     "as a signed fraction.")
    config_cls = ConstraintReleaseConfig

    def generate_entry(self):
        for _ in range(40):
            n = random.randint(self.config.n_min, self.config.n_max)
            max_pins = min(self.config.max_pins, n - 2)
            if max_pins < 1:
                continue
            n_pins = random.randint(1, max_pins)
            pinned = set(random.sample(range(n), n_pins))
            loads = [
                random.choice([-1, 1]) * random.randint(1, self.config.max_load)
                for _ in range(n)
            ]
            old = _equilibrium(loads, pinned)
            k0 = random.choice(sorted(pinned))
            pinned2 = pinned - {k0}
            new = _equilibrium(loads, pinned2)
            delta = new[k0] - old[k0]
            if delta == 0:
                continue
            num = int(sp.numer(delta))
            den = int(sp.denom(delta))
            break
        else:
            raise RuntimeError("could not build a nontrivial instance")

        answer = _fmt(delta)
        metadata = {
            "n": n,
            "loads": loads,
            "pinned": sorted(pinned),
            "released": int(k0),
            "old_disp": [_fmt(v) for v in old],
            "new_disp": [_fmt(v) for v in new],
            "change_num": num,
            "change_den": den,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        pins = ", ".join("mass %d" % i for i in metadata["pinned"])
        loads = ", ".join(
            "mass %d: %s" % (i, _fmt(l)) for i, l in enumerate(metadata["loads"])
        )
        r = metadata["released"]
        return (
            "Consider a horizontal chain of %d identical masses m0..m%d connected in "
            "series by identical springs of stiffness 1, with spring 0 anchored to a "
            "fixed wall at displacement 0 and spring %d anchoring the right end to a "
            "fixed wall at displacement 0. The following horizontal loads act on the "
            "masses: %s. The structure is additionally held by rigid support pins that "
            "keep the listed masses fixed at displacement 0: %s. Find the displacement "
            "of every mass that minimizes total potential energy (half the sum over "
            "springs of squared length-change, minus the work done by the loads). "
            "Now one of the support pins, the one on mass %d, is released so that mass "
            "%d becomes free to move while all loads and remaining pins stay as they "
            "are. The structure re-equilibrates to the new minimum-energy state. "
            "What is the change in the displacement of mass %d (new equilibrium value "
            "minus old equilibrium value)? Give the answer as a signed fraction or "
            "integer, e.g. a/b or -3/2 or 0."
            % (metadata["n"], metadata["n"] - 1, metadata["n"] - 1, loads, pins, r, r, r)
        )

    def distractor_candidates(self, entry):
        delta = sp.Rational(entry.metadata["change_num"], entry.metadata["change_den"])
        base = [entry.metadata["change_num"], entry.metadata["change_den"]]
        cands = [
            _fmt(-delta),
            _fmt(delta + 1),
            _fmt(sp.Rational(sp.numer(delta), sp.denom(delta) + 1)),
        ]
        m = entry.metadata
        cands.append(_fmt(sp.Rational(m["new_disp"][m["released"]])))
        seen = set()
        out = []
        for c in cands:
            if c not in seen and c != entry.answer:
                seen.add(c)
                out.append(c)
        return out

    def score_answer(self, answer, entry):
        gold = sp.Rational(entry.metadata["change_num"], entry.metadata["change_den"])
        got = _parse_fraction(answer)
        if got is None:
            return 0.0
        return 1.0 if got == gold else 0.0


def _parse_fraction(answer):
    if not isinstance(answer, str):
        return None
    a = answer.strip()
    if not a:
        return None
    try:
        r = sp.Rational(a)
    except Exception:
        return None
    if sp.denom(r) < 0:
        r = _fmt(r)
        return None
    return r


def _parse_fraction_answer(answer):
    got = _parse_fraction(answer)
    if got is None:
        return None
    return sp.numer(got), sp.denom(got)


TASK_META = {'parent_source_id': None,
 'idea': 'constraint_release_response (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/constraint_release_response',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
