import random

from reasoning_core.tasks.generated.k3_semantics_preserving_translation_r1.bayesian_network_table_conversion.bayesian_network_table_conversion import (
    BayesianNetworkTableConversion,
)


def test_basic_roundtrip():
    random.seed(42)
    task = BayesianNetworkTableConversion()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_wrong_answer_scores_zero():
    random.seed(7)
    task = BayesianNetworkTableConversion()
    x = task.generate_example()
    assert task.score_answer("999/1", x) == 0.0


def test_garbage_does_not_crash():
    random.seed(1)
    task = BayesianNetworkTableConversion()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("abc", x) == 0.0
    assert task.score_answer(None, x) == 0.0


def test_answer_in_unit_interval():
    random.seed(3)
    task = BayesianNetworkTableConversion()
    for _ in range(20):
        x = task.generate_example()
        r = __import__("sympy").Rational(x.answer)
        assert 0 <= r <= 1


def test_difficulty_changes():
    task = BayesianNetworkTableConversion()
    base = task.config.n_nodes
    task.config.set_level(5)
    assert task.config.n_nodes >= base
