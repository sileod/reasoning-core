import random

from sympy import Rational, Symbol

from reasoning_core.tasks.generated.k3_state_tracking_r4.dual_number_evaluation.dual_number_evaluation import (
    DualNumberEvaluation, DualNumberConfig, _render_poly, _coef_str, _fmt_pair
)

_X = Symbol('x')


def test_generate_scores_self():
    random.seed(1339177894)
    t = DualNumberEvaluation()
    for _ in range(20):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_answer_field_matches_answer():
    random.seed(7)
    t = DualNumberEvaluation()
    for _ in range(20):
        e = t.generate_entry()
        value = Rational(e.metadata.value)
        deriv = Rational(e.metadata.deriv)
        assert e.answer == _fmt_pair(value, deriv)
        assert e.answer == f'{_coef_str(value)}; {_coef_str(deriv)}'


def test_answer_is_true_evaluation():
    random.seed(11)
    t = DualNumberEvaluation()
    for _ in range(30):
        e = t.generate_entry()
        p_coeffs = [Rational(c) for c in e.metadata.p_coeffs]
        q_coeffs = [Rational(c) for c in e.metadata.q_coeffs]
        x0 = Rational(e.metadata.point)
        P = sum(c * _X ** i for i, c in enumerate(p_coeffs))
        Q = sum(c * _X ** i for i, c in enumerate(q_coeffs))
        p0 = P.subs(_X, x0)
        q0 = Q.subs(_X, x0)
        value = Rational(p0, q0)
        num = (P.diff(_X) * Q - P * Q.diff(_X)).subs(_X, x0)
        deriv = Rational(num, q0 * q0)
        expected = _fmt_pair(value, deriv)
        assert e.answer == expected
        assert q0 != 0


def test_domain_validation():
    random.seed(3)
    t = DualNumberEvaluation()
    for _ in range(20):
        e = t.generate_entry()
        q_coeffs = [Rational(c) for c in e.metadata.q_coeffs]
        x0 = Rational(e.metadata.point)
        Q = sum(c * _X ** i for i, c in enumerate(q_coeffs))
        assert Q.subs(_X, x0) != 0


def test_wrong_answers_score_zero():
    random.seed(3)
    t = DualNumberEvaluation()
    e = t.generate_example()
    assert t.score_answer('0; 0', e) == 0.0
    assert t.score_answer('', e) == 0.0
    assert t.score_answer('garbage', e) == 0.0


def test_difficulty_changes_config():
    cfg = DualNumberConfig()
    base = (cfg.max_deg, cfg.coeff_range, cfg.den_scale, cfg.point_den)
    cfg2 = DualNumberConfig()
    cfg2.apply_difficulty(5)
    assert base != (cfg2.max_deg, cfg2.coeff_range, cfg2.den_scale, cfg2.point_den)


def test_render_poly_roundtrip_nonempty():
    assert _render_poly([Rational(0)]) == '0'
    assert _render_poly([Rational(2, 1), Rational(3, 2), Rational(1)]) == 'x^2+3/2x+2'
