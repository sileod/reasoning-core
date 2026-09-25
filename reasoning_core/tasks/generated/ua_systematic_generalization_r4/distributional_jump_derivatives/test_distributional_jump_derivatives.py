from fractions import Fraction
from math import comb

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.distributional_jump_derivatives.distributional_jump_derivatives import (
    DistributionalJumpDerivatives,
    DistributionalJumpConfig,
    build_answer,
    _eval,
    _nderiv,
)


def _fs(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _make_entry(breaks, polys, n):
    res_polys = [_nderiv(p, n) for p in polys]
    return Entry(
        metadata={
            "breaks": [_fs(b) for b in breaks],
            "orig_polys": [[_fs(c) for c in p] for p in polys],
            "res_polys": [[_fs(c) for c in p] for p in res_polys],
            "deltas": [],
            "deriv_order": n,
        },
        answer="",
    )


def _raw_deltas(polys, breaks, n):
    out = []
    for i in range(len(polys) - 1):
        b = breaks[i]
        for m in range(n):
            jump = _eval(_nderiv(polys[i + 1], m), b) - _eval(_nderiv(polys[i], m), b)
            if jump != 0:
                out.append((comb(n - 1, m) * jump, n - 1 - m))
    return out


def test_first_derivative_delta():
    # f = (x^2 on -inf..0), (x+1 on 0..inf): f' = 1*delta(x)
    breaks = [Fraction(0)]
    polys = [[Fraction(0), Fraction(0), Fraction(1)],
             [Fraction(1), Fraction(1)]]
    n = 1
    deltas = _raw_deltas(polys, breaks, n)
    assert deltas == [(Fraction(1), 0)]


def test_second_derivative_deltas():
    # f above; f'' = delta(x) (jump in f') + delta'(x) (jump in f)
    breaks = [Fraction(0)]
    polys = [[Fraction(0), Fraction(0), Fraction(1)],
             [Fraction(1), Fraction(1)]]
    n = 2
    deltas = _raw_deltas(polys, breaks, n)
    assert deltas == [(Fraction(1), 1), (Fraction(1), 0)]


def test_reducible_weights():
    # f = (2x on -inf..1), (3x on 1..inf): jump f(1)=3*1-2*1=1, coefficient = 1
    breaks = [Fraction(1)]
    polys = [[Fraction(0), Fraction(2)],
             [Fraction(0), Fraction(3)]]
    n = 1
    deltas = _raw_deltas(polys, breaks, n)
    assert deltas == [(Fraction(1), 0)]


def test_negative_weight():
    breaks = [Fraction(2, 3)]
    polys = [[Fraction(1), Fraction(1)],
             [Fraction(0, 1), Fraction(2)]]
    n = 1
    deltas = _raw_deltas(polys, breaks, n)
    # jump = (0+2*2/3) - (1+2/3) = 4/3 - 5/3 = -1/3
    assert deltas[0][0] == Fraction(-1, 3)


def test_generate_scores_roundtrip():
    import random
    random.seed(7)
    task = DistributionalJumpDerivatives()
    cfg = DistributionalJumpConfig()
    cfg.apply_difficulty(0)
    task.config = cfg
    e = task.generate_entry()
    assert task.score_answer(e.answer, e) == 1.0
    assert task.score_answer("junk", e) == 0.0
    assert task.score_answer("", e) == 0.0
    assert build_answer(e.metadata) == e.answer
    assert task.render_prompt(e.metadata)


def test_every_level_scores():
    import random
    random.seed(3)
    for lev in (0, 1, 2, 3, 4, 5, 6):
        random.seed(100 + lev)
        task = DistributionalJumpDerivatives()
        cfg = DistributionalJumpConfig()
        cfg.apply_difficulty(lev)
        task.config = cfg
        for _ in range(8):
            e = task.generate_entry()
            assert task.score_answer(e.answer, e) == 1.0
