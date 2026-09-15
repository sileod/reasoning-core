import random

from reasoning_core.tasks.generated.k3_verification_repair_r1.simplex_pivot_execution.simplex_pivot_execution import (
    SimplexPivotExecution,
)


def test_generate_and_score():
    random.seed(1)
    task = SimplexPivotExecution()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_difficulty_changes():
    task = SimplexPivotExecution()
    task.config.set_level(0)
    l0 = (task.config.num_vars, task.config.num_constraints, task.config.coeff_range)
    task.config.set_level(6)
    l6 = (task.config.num_vars, task.config.num_constraints, task.config.coeff_range)
    assert l6 != l0


def test_score_rejects_junk():
    task = SimplexPivotExecution()
    ex = task.generate_example()
    assert task.score_answer("junk", ex) == 0.0
    assert task.score_answer("", ex) == 0.0


def test_answer_is_plausible_rational():
    random.seed(7)
    task = SimplexPivotExecution()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(15):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert ex.answer != "0"
            from sympy import Rational
            wrong = str(Rational(float(Rational(ex.answer)) + 1.0))
            assert task.score_answer(wrong, ex) == 0.0


def test_every_level_generates():
    random.seed(11)
    task = SimplexPivotExecution()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(3):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
