import random

import pytest

from .xor_peeling_recovery import (
    XORPeelingRecovery,
    is_valid_peel_order,
    peel_order,
)


def test_peel_order_evicts_singleton():
    # s0 alone in a check is recovered first; then s1 is exposed by removing s0.
    supports = [(0,), (0, 1)]
    assert peel_order(supports) == [0, 1]


def test_peel_order_tie_break_smallest_index():
    # Two singletons available at once; smallest index goes first.
    supports = [(2,), (1,), (3,)]
    assert peel_order(supports) == [1, 2, 3]


def test_peel_order_tie_break_after_recovery():
    # Recovering 0 leaves both {1} and {2}; pick 1 before 2.
    supports = [(0, 1), (0, 2), (0,)]
    assert peel_order(supports)[0] == 0
    assert set(peel_order(supports)[1:]) == {1, 2}


def test_unrecovered_symbols_absent():
    # s3 is never the sole member of a check, so it is not peeled.
    supports = [(0,), (0, 1, 3)]
    assert peel_order(supports) == [0]


def test_verify_accepts_correct_rejects_wrong():
    supports = [(0, 1), (1, 2), (2,)]
    order = peel_order(supports)
    assert is_valid_peel_order(supports, order)
    assert not is_valid_peel_order(supports, [0, 1, 2])


def test_generation_levels():
    task = XORPeelingRecovery()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        assert ex.answer == " ".join(ex.metadata["order"])
        assert task.score_answer(ex.answer, ex) == 1.0
        assert len(ex.metadata["order"]) >= 2
        assert str(ex.answer).strip() != ""


def test_score_rejects_junk():
    task = XORPeelingRecovery()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("s9 s9 s9", ex) < 1.0
    assert task.score_answer("not an answer", ex) < 1.0


def test_gold_equals_independent_recompute():
    import random as _r
    _r.seed(12345)
    task = XORPeelingRecovery()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(50):
            ex = task.generate_example()
            supports = [tuple(c["symbols"]) for c in ex.metadata["checks"]]
            ref = ["s%d" % i for i in peel_order(supports)]
            assert ex.answer == " ".join(ref)
            assert ex.metadata["order"] == ref


def test_no_global_reseed():
    task = XORPeelingRecovery()
    task.generate_example()
    a = random.random()
    task.generate_example()
    b = random.random()
    assert a != b
