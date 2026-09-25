import random

import sympy as sp

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_systematic_generalization_r4.asymptotic_cancellation_order.asymptotic_cancellation_order import (
    AsymptoticCancellationOrder,
    _survivor,
)


def test_generate_and_score():
    task = AsymptoticCancellationOrder()
    for level in (0, 2, 5):
        task.config.set_level(level)
        x = task.generate_example()
        assert isinstance(x, Entry)
        assert task.score_answer(x.answer, x) == 1.0
        assert task.score_answer("", x) == 0.0
        assert task.score_answer("junk", x) == 0.0
        assert task.score_answer("3, 1/2", x) in (0.0, 1.0)


def test_scorer_rejects_wrong():
    task = AsymptoticCancellationOrder()
    task.config.set_level(3)
    x = task.generate_example()
    for wrong in (
        "5, 1",
        "-1, 7/3",
        "0, 0",
        str(x.metadata["exp"]) + ", 999",
    ):
        if wrong != x.answer:
            assert task.score_answer(wrong, x) == 0.0, wrong


def test_first_survivor_is_consistent():
    x = sp.symbols("x")
    task = AsymptoticCancellationOrder()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            expr = sp.S(ex.metadata["expression"])
            n = ex.metadata["order"]
            surv = _survivor(expr, x, n + 6)
            assert surv is not None
            assert surv[0] == ex.metadata["exp"]
            assert sp.Rational(surv[1]) == sp.Rational(
                ex.metadata["coeff_num"], ex.metadata["coeff_den"]
            ), (ex.metadata["expression"], ex.answer)


def test_difficulty_changes():
    task = AsymptoticCancellationOrder()
    task.config.set_level(0)
    a0 = task.config.base_level
    task.config.set_level(5)
    a5 = task.config.base_level
    assert a5 > a0
