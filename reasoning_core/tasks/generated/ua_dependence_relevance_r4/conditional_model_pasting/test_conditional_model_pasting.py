import random

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.conditional_model_pasting.conditional_model_pasting import (
    ConditionalModelPasting,
)


def test_generate_and_score_default():
    task = ConditionalModelPasting()
    for _ in range(20):
        x = task.generate_example()
        assert x.answer in ("yes", "no")
        assert task.score_answer(x.answer, x) == 1.0


def test_score_rejects_junk():
    task = ConditionalModelPasting()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("maybe", x) == 0.0
    assert task.score_answer(x.answer.upper(), x) == 1.0


def test_difficulty_changes_config():
    task = ConditionalModelPasting()
    c0 = task.config.level
    task.config.set_level(0)
    r0 = task.config.r_state
    task.config.set_level(6)
    assert c0 >= 0
    assert task.config.r_state >= r0


def test_balanced_labels():
    task = ConditionalModelPasting()
    counts = {"yes": 0, "no": 0}
    for _ in range(40):
        x = task.generate_example()
        counts[x.answer] += 1
    assert counts["no"] >= 10 and counts["yes"] >= 10


def test_all_levels_generate():
    task = ConditionalModelPasting()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(5):
            x = task.generate_example()
            assert x.answer in ("yes", "no")
