import random
from dataclasses import dataclass
from fractions import Fraction
from math import comb

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _fs(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _term(coeff, power, var):
    if coeff == 0:
        return ""
    c = Fraction(coeff)
    if power == 0:
        return _fs(c)
    base = var if power == 1 else f"{var}^{power}"
    if c == 1:
        return base
    if c == -1:
        return f"-{base}"
    if c < 0:
        mag = _fs(-c)
        if Fraction(-c).denominator != 1:
            return f"-({mag}){base}"
        return f"-{mag}{base}"
    mag = _fs(c)
    if Fraction(c).denominator != 1:
        return f"({mag}){base}"
    return f"{mag}{base}"


def _poly(coeffs, var):
    terms = []
    for power in range(len(coeffs) - 1, -1, -1):
        c = Fraction(coeffs[power])
        if c != 0:
            terms.append(_term(c, power, var))
    if not terms:
        return "0"
    out = terms[0]
    for t in terms[1:]:
        if t.startswith("-"):
            out += " - " + t[1:]
        else:
            out += " + " + t
    return out


def _derive(coeffs):
    if len(coeffs) <= 1:
        return [Fraction(0)]
    return [Fraction(coeffs[p]) * p for p in range(1, len(coeffs))]


def _nderiv(coeffs, m):
    c = [Fraction(x) for x in coeffs]
    for _ in range(m):
        c = _derive(c)
    return c


def _eval(coeffs, x):
    s = Fraction(0)
    for p in range(len(coeffs)):
        s += Fraction(coeffs[p]) * (x ** p)
    return s


def _intervals(breaks):
    return [None] + list(breaks) + [None]


def _piece_str(lo, hi, poly, var):
    lo_s = "-inf" if lo is None else _fs(lo)
    hi_s = "inf" if hi is None else _fs(hi)
    return f"({lo_s}, {hi_s}): {_poly(poly, var)}"


def _render_deltas(delta_list, var):
    """delta_list: iterable of (breakpoint, coeff(Fraction), order), not sorted.
    Returns the canonical ' + ' (or ' - ') joined delta string."""
    items = sorted(delta_list, key=lambda t: (t[0], t[2]))
    parts = []
    for (b, coeff, order) in items:
        c = Fraction(coeff)
        if c == 0:
            continue
        d = "'" * order
        mag = _fs(abs(c))
        if c > 0:
            parts.append((1, f"{mag}*delta{d}({var}-{_fs(b)})"))
        else:
            parts.append((-1, f"{mag}*delta{d}({var}-{_fs(b)})"))
    if not parts:
        return ""
    out = parts[0][1]
    if parts[0][0] < 0:
        out = "-" + out
    for sign, s in parts[1:]:
        out += " - " + s if sign < 0 else " + " + s
    return out


class DistributionalJumpConfig(Config):
    pieces: int = 2
    max_degree: int = 2
    deriv_order: int = 1
    coeff_denom: int = 3

    def apply_difficulty(self, level):
        self.pieces = 2 + (level >= 2)
        self.max_degree = 2 + (level >= 1) + (level >= 4)
        self.deriv_order = 1 + (level >= 2) + (level >= 5)
        self.coeff_denom = 2 + (level >= 3)


class DistributionalJumpDerivatives(Task):
    summary = (
        "Differentiate piecewise polynomial functions and point-supported distributions "
        "across repeated derivatives; combine ordinary derivatives with jump-induced "
        "delta terms, returning the resulting distribution."
    )
    design_choice = (
        "Instances specify breakpoints as rationals and ask for the distributional "
        "derivative as a canonical sum of piecewise polynomial terms plus weighted "
        "Dirac deltas at each breakpoint, with weights as reduced fractions."
    )
    config_cls = DistributionalJumpConfig

    def _rand_frac(self):
        num = random.randint(-6, 6)
        if num == 0:
            denom = 1
        else:
            denom = random.randint(1, self.config.coeff_denom)
        return Fraction(num, denom)

    def _gen_polys(self, count):
        polys = []
        for _ in range(count):
            deg = random.randint(0, self.config.max_degree)
            polys.append([self._rand_frac() for _ in range(deg + 1)])
        return polys

    def _gen_breaks(self, count):
        breaks = set()
        guard = 0
        while len(breaks) < count and guard < 400:
            guard += 1
            breaks.add(Fraction(random.randint(-2, 4), random.randint(1, 2)))
        return sorted(breaks)

    def generate_entry(self):
        nbr = self.config.pieces
        while True:
            breaks = self._gen_breaks(nbr - 1)
            if len(breaks) == nbr - 1:
                break
        polys = self._gen_polys(nbr)
        n = self.config.deriv_order

        res_polys = [_nderiv(p, n) for p in polys]
        delta_list = []
        for i in range(len(polys) - 1):
            b = breaks[i]
            for m in range(n):
                jump = _eval(_nderiv(polys[i + 1], m), b) - _eval(_nderiv(polys[i], m), b)
                if jump != 0:
                    coeff = comb(n - 1, m) * jump
                    delta_list.append((b, coeff, n - 1 - m))

        var = "x"
        intervals = _intervals(breaks)
        ans_pieces = [_piece_str(intervals[i], intervals[i + 1], res_polys[i], var)
                      for i in range(nbr)]

        delta_str = _render_deltas(delta_list, var)
        answer = "; ".join(ans_pieces)
        if delta_str:
            answer += "; DELTAS: " + delta_str

        metadata = {
            "breaks": [_fs(b) for b in breaks],
            "orig_polys": [[_fs(c) for c in p] for p in polys],
            "res_polys": [[_fs(c) for c in p] for p in res_polys],
            "deltas": [[_fs(b), _fs(c), order] for (b, c, order) in delta_list],
            "deriv_order": n,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        var = "x"
        breaks = [Fraction(s) for s in metadata["breaks"]]
        polys = [[Fraction(s) for s in p] for p in metadata["orig_polys"]]
        n = metadata["deriv_order"]

        intervals = _intervals(breaks)
        pieces = "; ".join(
            "on " + _piece_str(intervals[i], intervals[i + 1], polys[i], var)
            for i in range(len(polys))
        )
        ordinal = {1: "first", 2: "second", 3: "third"}.get(n, f"{n}-th")
        return (
            f"Let f be the piecewise polynomial function (a distribution) on the real "
            f"line defined as follows: {pieces}. "
            f"Compute the {ordinal} distributional derivative f^({n}) as a distribution. "
            f"Write the answer as a canonical sum: first the piecewise polynomial part, "
            f"with the polynomial on each interval in reduced form (e.g. "
            f"'(-inf, 2/3): 2x^2 - 3x + 1/2'), the intervals separated by '; ', and "
            f"then, if any, the weighted Dirac delta terms at the breakpoints, after "
            f"'DELTAS: ', each as weight*delta(x-b), weight*delta'(x-b) for the first "
            f"derivative of the delta, delta'' for the second, and so on, the terms "
            f"joined with ' + ', all weights as reduced fractions and breakpoints as "
            f"rationals."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            gold = build_answer(entry.metadata)
        except Exception:
            return 0.0
        return 1.0 if _ws(answer) == _ws(gold) else 0.0


def _ws(s):
    return "".join(s.split())


def build_answer(metadata):
    var = "x"
    breaks = [Fraction(s) for s in metadata["breaks"]]
    res_polys = metadata["res_polys"]
    delta_list = metadata["deltas"]

    intervals = _intervals(breaks)
    ans_pieces = [_piece_str(intervals[i], intervals[i + 1], res_polys[i], var)
                  for i in range(len(res_polys))]

    delta_list = [(Fraction(bs), Fraction(cs), order) for (bs, cs, order) in delta_list]
    delta_str = _render_deltas(delta_list, var)

    answer = "; ".join(ans_pieces)
    if delta_str:
        answer += "; DELTAS: " + delta_str
    return answer


TASK_META = {'parent_source_id': None,
 'idea': 'distributional_jump_derivatives (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/distributional_jump_derivatives',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
