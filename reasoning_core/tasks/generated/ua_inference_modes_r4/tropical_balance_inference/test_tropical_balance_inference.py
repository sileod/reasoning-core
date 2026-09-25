import random

import pytest

from reasoning_core.template import _ROUNDING_SEED

from .tropical_balance_inference import (
    TropicalBalanceConfig,
    TropicalBalanceInference,
    _parse_tuple,
    _weight,
)


def _system_ok(eq, a, b):
    w12 = _weight(a, b, eq["k1"], eq["p1"], eq["q1"])
    w2 = _weight(a, b, eq["k2"], eq["p2"], eq["q2"])
    w3 = _weight(a, b, eq["k3"], eq["p3"], eq["q3"])
    return abs(w12 - w2) <= 0 and w3 < w12 - 1e-9


def test_gold_balances_both_equations():
    task = TropicalBalanceInference()
    for _ in range(50):
        ex = task.generate_example()
        a, b = ex.metadata["a"], ex.metadata["b"]
        assert _system_ok(ex.metadata["eq1"], a, b)
        assert _system_ok(ex.metadata["eq2"], a, b)


def test_score_round_trip():
    task = TropicalBalanceInference()
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("junk", ex) == 0.0
        assert task.score_answer("(999, 999)", ex) == 0.0


def test_parse_tuple_forms():
    assert _parse_tuple("(3, 2)") == (3, 2)
    assert _parse_tuple("3 2") == (3, 2)
    assert _parse_tuple("[3,2]") == (3, 2)
    assert _parse_tuple("3, 2") == (3, 2)
    assert _parse_tuple("( 3 , -2 )") == (3, -2)
    assert _parse_tuple("banana") is None


def test_difficulty_changes_config():
    cfg = TropicalBalanceConfig()
    cfg.set_level(0)
    base = (cfg.exp_range, cfg.val_range, cfg.max_ab)
    cfg.set_level(6)
    hi = (cfg.exp_range, cfg.val_range, cfg.max_ab)
    assert all(h > b for h, b in zip(hi, base))


def test_all_levels_generate_and_score():
    task = TropicalBalanceInference()
    for level in range(7):
        for _ in range(5):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0
            a, b = ex.metadata["a"], ex.metadata["b"]
            assert a >= 0 and b >= 0


def test_answers_vary():
    task = TropicalBalanceInference()
    seen = set()
    for _ in range(40):
        ex = task.generate_example()
        seen.add(ex.answer)
    assert len(seen) > 1
