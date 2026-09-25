import random
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt

from reasoning_core.template import Config, Entry, Task


def _valid_grid(ax, by, e):
    """2x2 grid g[x][y] of Fractions with E[X]=ax, E[Y]=by, E[XY]=e, or None."""
    if e < 0 or e > ax or e > by or e < ax + by - 1:
        return None
    g = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
    g[1][1] = e
    g[1][0] = ax - e
    g[0][1] = by - e
    g[0][0] = 1 - ax - by + e
    if any(v < 0 or v > 1 for row in g for v in row):
        return None
    return g


def _moments(g):
    a = g[1][0] + g[1][1]
    b = g[0][1] + g[1][1]
    c = g[1][1]
    return a, b, c


def _cov_poly(g0, g1):
    a0, b0, c0 = _moments(g0)
    a1, b1, c1 = _moments(g1)
    da = a0 - a1
    db = b0 - b1
    A = -da * db
    B = c0 - c1 - a1 * db - da * b1
    C = c1 - a1 * b1
    return A, B, C


def _sqrt_fraction(f):
    n = f.numerator
    d = f.denominator
    sn = isqrt(n)
    sd = isqrt(d)
    if sn * sn == n and sd * sd == d:
        return Fraction(sn, sd)
    return None


def _rational_roots(A, B, C):
    if A == 0:
        if B == 0:
            return None
        return [Fraction(-C, B)]
    D = B * B - 4 * A * C
    if D < 0:
        return []
    s = _sqrt_fraction(D)
    if s is None:
        return None
    r1 = (-B + s) / (2 * A)
    r2 = (-B - s) / (2 * A)
    return sorted(set([r1, r2]))


def interior_roots(A, B, C):
    roots = _rational_roots(A, B, C)
    if roots is None:
        return None
    return [r for r in roots if Fraction(0) < r < Fraction(1)]


def _make_stratum(w, denom_max):
    omw = 1 - w
    for _ in range(200):
        D = random.randint(2, denom_max)
        u = Fraction(random.randint(1, D - 1), D)
        v = Fraction(random.randint(1, D - 1), D)
        M = _valid_grid(u, v, u * v)
        D1 = random.randint(2, denom_max)
        ax = Fraction(random.randint(1, D1 - 1), D1)
        by = Fraction(random.randint(1, D1 - 1), D1)
        lo = max(Fraction(0), ax + by - 1)
        hi = min(ax, by)
        e = None
        for _ in range(30):
            e_den = random.randint(1, denom_max)
            cand = Fraction(random.randint(0, e_den), e_den)
            if lo <= cand <= hi:
                e = cand
                break
        if e is None:
            continue
        P1 = _valid_grid(ax, by, e)
        if P1 is None:
            continue
        P0 = [[(M[i][j] - omw * P1[i][j]) / w for j in range(2)] for i in range(2)]
        if any(v < 0 or v > 1 for row in P0 for v in row):
            continue
        A, B, C = _cov_poly(P0, P1)
        ints = interior_roots(A, B, C)
        if ints == [w]:
            return P0, P1
    return None


def _fmt(grid):
    cells = []
    for x in (0, 1):
        for y in (0, 1):
            cells.append(f"X={x},Y={y}: {grid[x][y].numerator}/{grid[x][y].denominator}")
    return "; ".join(cells)


@dataclass
class MixtureConfig(Config):
    strata: int = 1
    denom_max: int = 5

    def apply_difficulty(self, level):
        self.strata = min(1 + level, 5)
        self.denom_max = 5 + level


class IndependenceRestoringMixtures(Task):
    summary = ("Mix pairs of finite binary joint distributions with an unknown rational "
               "weight, including mixtures inside conditioning strata with a shared weight; "
               "find the unique weight 0<w<1 that makes the designated variables independent "
               "or conditionally independent given a grouping.")
    config_cls = MixtureConfig

    def generate_entry(self):
        strata = self.config.strata
        denom_max = self.config.denom_max
        for _ in range(40):
            D = random.randint(2, denom_max)
            w = Fraction(random.randint(1, D - 1), D)
            grids = []
            ok = True
            for _ in range(strata):
                pair = _make_stratum(w, denom_max)
                if pair is None:
                    ok = False
                    break
                grids.append(pair)
            if not ok:
                continue
            p0s = [g[0] for g in grids]
            p1s = [g[1] for g in grids]
            for g0, g1 in zip(p0s, p1s):
                A, B, C = _cov_poly(g0, g1)
                if interior_roots(A, B, C) != [w]:
                    ok = False
                    break
            if not ok:
                continue
            n, d = w.numerator, w.denominator
            metadata = {
                "strata": [[[_fmt(g0)], [_fmt(g1)]] for g0, g1 in zip(p0s, p1s)],
                "conditional": strata > 1,
                "answer": f"{n}/{d}",
            }
            return Entry(metadata=metadata, answer=f"{n}/{d}")
        raise RuntimeError("could not construct an independence-restoring mixture instance")

    def render_prompt(self, metadata):
        s = metadata["strata"]
        if metadata["conditional"]:
            lines = [
                "Two statisticians each propose a joint distribution over binary variables X and Y "
                "given a conditioning variable Z with equally likely levels."
            ]
            for z, (p0, p1) in enumerate(s):
                lines.append(
                    f"At level Z=z{z+1}: candidate distribution P0 gives {p0[0]}; "
                    f"candidate distribution P1 gives {p1[0]}."
                )
            lines.append(
                "A mixture of weight w draws from P0 and weight 1-w draws from P1, using the SAME "
                "rational weight w in every level, so within level z the joint is M_z = w*P0 + (1-w)*P1. "
                "Find the unique rational weight w with 0<w<1 such that X and Y are conditionally "
                "independent given Z (independent within every level simultaneously). "
                "Give w as a fraction a/b in lowest terms, e.g. 3/5."
            )
            return "\n".join(lines)
        p0, p1 = s[0][0][0], s[0][1][0]
        return (
            "Two statisticians each propose a joint distribution over binary variables X and Y. "
            f"Candidate distribution P0 gives {p0}; candidate distribution P1 gives {p1}. "
            "You fit a mixture P = w*P0 + (1-w)*P1 with unknown rational weight w. "
            "Find the unique rational weight w with 0<w<1 such that X and Y are independent under P. "
            "Give w as a fraction a/b in lowest terms, e.g. 3/5."
        )

    def score_answer(self, answer, entry):
        try:
            got = Fraction(str(answer).strip())
        except Exception:
            return 0.0
        try:
            gold = Fraction(entry.metadata["answer"])
        except Exception:
            return 0.0
        return 1.0 if got == gold else 0.0


TASK_META = {
    'parent_source_id': None,
    'idea': 'independence_restoring_mixtures (variant 3 of 3, unguided baseline)',
    'hypothesis': 'P009',
    'changes': 'new task in reasoning_core/tasks/generated/ua_dependence_relevance_r4/independence_restoring_mixtures',
    'generation': {
        'provider_name': 'albert',
        'model_name': 'deepseek-v4-flash',
        'harness_name': 'opencode',
        'harness_version': '1.18.32',
        'agent_name': 'task-search-worker',
        'settings': {
            'variant': None,
            'requested_seed': 3713447331,
            'seed_forwarded': True,
            'temperature': None,
            'top_p': None,
            'pure': True,
            'max_steps': 56,
            'timeout_seconds': 1800,
            'sandbox': {'name': 'bubblewrap', 'version': 'bubblewrap 0.8.0'},
        },
    },
}
