import random

from reasoning_core.tasks.generated.ua_interacting_updates_r5.substitution_uniform_recurrence.substitution_uniform_recurrence import (
    SubstitutionUniformRecurrence,
)


def test_round_trip_yes():
    random.seed(1)
    task = SubstitutionUniformRecurrence()
    task.config.set_level(0)
    seen = {"yes": 0, "no": 0}
    for _ in range(20):
        x = task.generate_example()
        assert x.answer in ("yes", "no")
        assert task.score_answer(x.answer, x) == 1.0
        assert x.answer == x.metadata["recurrence"]
        seen[x.answer] += 1
    assert seen["yes"] > 0 and seen["no"] > 0, seen


def test_garbage_scores_zero():
    random.seed(2)
    task = SubstitutionUniformRecurrence()
    task.config.set_level(2)
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("maybe", x) == 0.0
    assert task.score_answer("YES", x) == (1.0 if x.answer == "yes" else 0.0)


def test_all_levels_generate():
    task = SubstitutionUniformRecurrence()
    for level in range(7):
        task.config.set_level(level)
        random.seed(10 + level)
        for _ in range(5):
            x = task.generate_example()
            assert x.answer in ("yes", "no")
            assert task.score_answer(x.answer, x) == 1.0


def test_difficulty_changes_config():
    task = SubstitutionUniformRecurrence()
    base = task.config.alphabet_size
    task.config.set_level(3)
    bigger = task.config.alphabet_size
    assert bigger >= base
