import random

from reasoning_core.tasks.generated.k3_language_implementation_r4.phi_sensitive_ssa.phi_sensitive_ssa import (
    PhiSensitiveSSA,
    _apply,
    _eval_expr,
)


def test_generate_example():
    t = PhiSensitiveSSA()
    e = t.generate_example()
    assert e.answer is not None


def test_score_gold():
    t = PhiSensitiveSSA()
    for _ in range(60):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0
        assert t.score_answer("", e) < 1.0
        assert t.score_answer("zzz", e) < 1.0


def test_apply():
    assert _apply(("add", "x", "c"), 3, 2) == 5
    assert _apply(("sub", "c", "x"), 3, 2) == -1
    assert _apply(("mul", "x", "c"), 3, 2) == 6


def test_eval_expr():
    assert _eval_expr(("add", "x", "x"), {"x": 4, "c": 9}) == 8
    assert _eval_expr(5, {"x": 4, "c": 9}) == 5


def test_all_levels():
    t = PhiSensitiveSSA()
    for lvl in range(0, 7):
        e = t.generate_example(level=lvl)
        assert m["level"] == lvl if (m := e.metadata) else True


def test_balanced_modes_are_present():
    t = PhiSensitiveSSA()
    modes = set()
    for _ in range(200):
        e = t.generate_example(level=5)
        modes.add(e.metadata["mode"])
    assert "value" in modes
    assert modes <= {"value", "phi", "invalid"}
