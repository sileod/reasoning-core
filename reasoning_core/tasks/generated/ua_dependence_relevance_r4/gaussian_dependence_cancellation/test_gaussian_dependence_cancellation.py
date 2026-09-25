import random

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.gaussian_dependence_cancellation.gaussian_dependence_cancellation import (
    GaussianDependenceCancellation,
)


def test_generate_and_score():
    task = GaussianDependenceCancellation()
    for _ in range(20):
        entry = task.generate_example()
        assert entry.answer in ("yes", "no")
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("maybe", entry) == 0.0


def test_difficulty_changes():
    task = GaussianDependenceCancellation()
    c0 = task.config.n
    task.config.set_level(6)
    assert task.config.n > c0


def test_balance():
    task = GaussianDependenceCancellation()
    random.seed(0)
    yes = 0
    total = 50
    for _ in range(total):
        entry = task.generate_example()
        if entry.answer == "yes":
            yes += 1
    assert 0 < yes < total
