import random

from reasoning_core.tasks.generated.k3_language_implementation_r4.query_cardinality_estimation.query_cardinality_estimation import (
    QueryCardinalityEstimation,
)


def test_gold_scoring_each_level():
    random.seed(12345)
    task = QueryCardinalityEstimation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_and_empty_scoring():
    random.seed(99)
    task = QueryCardinalityEstimation()
    task.config.set_level(3)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0
    assert task.score_answer(str(int(ex.answer) + 1), ex) == 0.0


def test_answer_in_domain():
    random.seed(7)
    task = QueryCardinalityEstimation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            ex = task.generate_example()
            assert int(ex.answer) >= 0


def test_difficulty_changes_structure():
    task = QueryCardinalityEstimation()
    base = task.config.ntables
    task.config.set_level(6)
    assert task.config.ntables >= base


def test_balance_of_answers():
    random.seed(2024)
    task = QueryCardinalityEstimation()
    task.config.set_level(2)
    answers = set()
    for _ in range(30):
        ex = task.generate_example()
        answers.add(ex.answer)
    assert len(answers) > 5


def test_answer_is_not_surface():
    random.seed(31)
    task = QueryCardinalityEstimation()
    task.config.set_level(2)
    for _ in range(20):
        ex = task.generate_example()
        sizes = list(ex.metadata['tables'].values())
        assert int(ex.answer) not in sizes


def test_bounded_at_all_levels():
    random.seed(5)
    task = QueryCardinalityEstimation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            n = int(ex.answer)
            assert 0 <= n <= 400 * (task.config.ntables) ** 3
