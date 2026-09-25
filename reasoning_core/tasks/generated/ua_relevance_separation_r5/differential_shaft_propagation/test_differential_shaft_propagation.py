"""Tests for differential_shaft_propagation."""

import random
from fractions import Fraction

from reasoning_core.tasks.generated.ua_relevance_separation_r5.differential_shaft_propagation.differential_shaft_propagation import (  # noqa: E501
    DifferentialShaftPropagation,
    solve,
    to_fraction,
    parse_answer,
)

TASK = DifferentialShaftPropagation


def test_roundtrip_fraction_reduced():
    assert to_fraction("3/2") == Fraction(3, 2)
    assert to_fraction("-4") == Fraction(-4, 1)
    assert to_fraction("6/4") == Fraction(3, 2)


def test_solve_consistent_chain():
    # shaft0 -> shaft1 external 30:15 reverses and halves? R = -30/15 = -2
    conns = [(0, 1, Fraction(-30, 15))]
    locked, values = solve(conns, 2)
    assert locked is False
    assert values[1] == Fraction(-2, 1)


def test_solve_detects_locked_loop():
    # triangle: 0-1 R=-1, 0-2 R=-1, 1-2 R=+1
    # 0-1: v1=-v0; 0-2: v2=-v0; 1-2: v2 must = v1 (R=+1) -> -v0 == -v0 ok.
    conns = [(0, 1, Fraction(-1)), (0, 2, Fraction(-1)), (1, 2, Fraction(1))]
    locked, values = solve(conns, 3)
    assert locked is False
    # now make 1-2 a flip: v2 must = -v1 -> -v0 == v0 -> inconsistent
    conns = [(0, 1, Fraction(-1)), (0, 2, Fraction(-1)), (1, 2, Fraction(-1))]
    locked, _ = solve(conns, 3)
    assert locked is True


def test_gold_scores_one():
    random.seed(12345)
    task = TASK()
    for _ in range(30):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    random.seed(999)
    task = TASK()
    for _ in range(30):
        entry = task.generate_example()
        assert task.score_answer("", entry) < 1.0
        assert task.score_answer(None, entry) < 1.0
        assert task.score_answer("garbage", entry) < 1.0


def test_metadata_json_serializable():
    import json

    random.seed(7)
    task = TASK()
    for _ in range(20):
        entry = task.generate_example()
        json.dumps(entry.metadata)


def test_all_levels_generate():
    random.seed(42)
    task = TASK()
    for lvl in range(7):
        task.config.set_level(lvl)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_both_outcomes_occur():
    random.seed(2024)
    task = TASK()
    locked = 0
    total = 0
    for lvl in (0, 2, 5):
        task.config.set_level(lvl)
        for _ in range(120):
            entry = task.generate_example()
            total += 1
            if entry.metadata["locked"]:
                locked += 1
    assert 0 < locked < total
