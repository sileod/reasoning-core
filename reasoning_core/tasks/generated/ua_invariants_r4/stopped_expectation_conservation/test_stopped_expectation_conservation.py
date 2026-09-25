import random
from fractions import Fraction

from reasoning_core.tasks.generated.ua_invariants_r4.stopped_expectation_conservation.stopped_expectation_conservation import (
    StoppedExpectationConservation as T,
    _harmonic_start,
    _parse_frac,
)


def test_harmonic_linear_interpolation():
    assert _harmonic_start(2, 1, 0, 3) == Fraction(1, 1)
    assert _harmonic_start(3, 2, 0, 4) == Fraction(2, 1)
    assert _harmonic_start(2, 2, 0, 3) == Fraction(2, 1)
    assert _harmonic_start(4, 3, 1, 2) == Fraction(8, 5)


def test_parse_frac():
    assert _parse_frac("2/3") == Fraction(2, 3)
    assert _parse_frac("5") == Fraction(5, 1)
    assert _parse_frac("garbage") is None
    assert _parse_frac("") is None
    assert _parse_frac("/") is None
    assert _parse_frac("2/0") is None


def test_gold_scores():
    task = T()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_entry()
            assert task.score_answer(e.answer, e) == 1.0


def test_junk_rejected():
    task = T()
    task.config.set_level(3)
    e = task.generate_entry()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer(" ", e) < 1.0
    assert task.score_answer("reajrjrje9595!", e) < 1.0
    assert task.score_answer("0/0", e) < 1.0
    assert task.score_answer("banana", e) < 1.0


def test_answer_in_domain():
    task = T()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(50):
            e = task.generate_entry()
            val = _parse_frac(e.answer)
            lo = min(e.metadata["a"], e.metadata["b"])
            hi = max(e.metadata["a"], e.metadata["b"])
            assert lo <= val <= hi
            assert Fraction(e.metadata["a"]) != Fraction(e.metadata["b"])


def test_level_changes_config():
    task = T()
    c0 = dict(task.config.to_dict())
    task.config.set_level(4)
    assert task.config != c0


def test_gold_not_equal_boundary():
    task = T()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(50):
            e = task.generate_entry()
            assert e.answer != str(e.metadata["a"])
            assert e.answer != str(e.metadata["b"])


def test_validate_passes():
    T().validate(n_samples=5)
