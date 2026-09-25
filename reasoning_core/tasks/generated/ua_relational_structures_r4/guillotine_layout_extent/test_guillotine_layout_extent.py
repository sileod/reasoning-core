import random

from reasoning_core.tasks.generated.ua_relational_structures_r4.guillotine_layout_extent.guillotine_layout_extent import (  # noqa
    GuillotineLayoutExtent,
    GuillotineLayoutExtentV2Config,
)


def test_generate_example():
    task = GuillotineLayoutExtent()
    x = task.generate_example()
    assert x.answer
    assert task.score_answer(x.answer, x) == 1.0
    assert "x" in x.answer


def test_score_gold_all_levels():
    task = GuillotineLayoutExtent()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(8):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
            assert task.score_answer("", x) < 1.0
            assert task.score_answer("junk", x) < 1.0


def test_difficulty_changes():
    task = GuillotineLayoutExtent()
    task.config.set_level(0)
    cfg0 = GuillotineLayoutExtentV2Config()
    task.config.set_level(6)
    assert task.config.leaves != cfg0.leaves


def test_answer_domain():
    task = GuillotineLayoutExtent()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(8):
            x = task.generate_example()
            w, h = x.answer.split("x")
            assert int(w) >= 1 and int(h) >= 1


def test_reproducible_with_fixed_seed():
    random.seed(1)
    task = GuillotineLayoutExtent()
    a = [task.generate_example().answer for _ in range(10)]
    random.seed(1)
    task2 = GuillotineLayoutExtent()
    b = [task2.generate_example().answer for _ in range(10)]
    assert a == b
