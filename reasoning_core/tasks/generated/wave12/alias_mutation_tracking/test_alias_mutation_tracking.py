import random

from reasoning_core.tasks.generated.wave12.alias_mutation_tracking.alias_mutation_tracking import (
    AliasMutationTracking,
)


def test_gold_scores_one():
    task = AliasMutationTracking()
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_less_than_one():
    task = AliasMutationTracking()
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("garbage", e) < 1.0


def test_answer_matches_metadata():
    task = AliasMutationTracking()
    for _ in range(50):
        e = task.generate_example()
        expected = f"get_value({e.metadata['query_name']}) => {e.metadata['answer_value']}"
        assert e.answer == expected


def test_difficulty_raises_ops():
    task = AliasMutationTracking()
    task.config.set_level(0)
    n0 = task.config.n_ops
    task.config.set_level(5)
    n5 = task.config.n_ops
    assert n5 > n0
