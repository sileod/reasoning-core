import random

import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_state_tracking_r5.mean_preserving_spread_order.mean_preserving_spread_order import (
    MeanPreservingSpreadOrder,
    _w1_fraction,
    _reduce,
    _parse_frac,
)


def _task(level=0):
    t = MeanPreservingSpreadOrder()
    t.config.set_level(level)
    return t


def test_uniform_benchmark_zero():
    assert _w1_fraction([0, 2], [1, 1]) == (0, 1)


def test_hand_computed():
    assert _w1_fraction([0, 2], [3, 1]) == (1, 2)


def test_reduce():
    assert _reduce(4, 6) == (2, 3)
    assert _reduce(0, 5) == (0, 1)


def test_parse_frac():
    assert _parse_frac("2/4") == (1, 2)
    assert _parse_frac("0") == (0, 1)


def test_generate_all_levels():
    for level in range(0, 7):
        t = _task(level)
        ex = t.generate_example()
        assert t.score_answer(ex.answer, ex) == 1.0


def test_config_changes_with_level():
    t0 = _task(0)
    t6 = _task(6)
    assert t6.config.span > t0.config.span
    assert t6.config.count >= t0.config.count


def test_answer_positive_domain():
    for level in range(0, 7):
        t = _task(level)
        for _ in range(20):
            ex = t.generate_example()
            p, q = _parse_frac(ex.answer)
            assert q > 0 and p >= 0


def test_junk_scores_zero():
    t = _task()
    ex = t.generate_example()
    assert t.score_answer("", ex) == 0.0
    assert t.score_answer("abc", ex) == 0.0
    assert t.score_answer("1", ex) == 0.0


def test_reproducible_with_seed():
    random.seed(1234)
    t = _task(3)
    a = t.generate_entry()
    random.seed(1234)
    t2 = _task(3)
    b = t2.generate_entry()
    assert a.answer == b.answer
    assert a.metadata["outcomes"] == b.metadata["outcomes"]


def test_answers_not_constant():
    t = _task(3)
    answers = {t.generate_entry().answer for _ in range(40)}
    assert len(answers) > 5


def test_weights_not_all_equal():
    t = _task(0)
    for _ in range(40):
        ex = t.generate_entry()
        assert len(set(ex.metadata["weights"])) > 1

