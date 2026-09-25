import random

from reasoning_core.tasks.generated.ua_latent_representation_r4.support_function_composition.support_function_composition import (
    SupportFunctionComposition,
)


def test_gold_answer_scores_one():
    task = SupportFunctionComposition()
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_scorer_rejects_junk():
    task = SupportFunctionComposition()
    e = task.generate_example()
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("abc", e) == 0.0
    assert task.score_answer("not a number", e) == 0.0


def test_wrong_answer_scores_zero():
    task = SupportFunctionComposition()
    e = task.generate_example()
    gold = int(e.answer)
    wrong = gold + 1
    assert task.score_answer(str(wrong), e) == 0.0


def test_difficulty_changes_config():
    task = SupportFunctionComposition()
    c0 = SupportFunctionComposition.config_cls()
    c0.set_level(0)
    c6 = SupportFunctionComposition.config_cls()
    c6.set_level(6)
    assert c6.n >= c0.n
    assert c6.depth >= c0.depth


def test_all_levels_generate():
    task = SupportFunctionComposition()
    for level in range(7):
        cfg = SupportFunctionComposition.config_cls()
        cfg.set_level(level)
        task.config = cfg
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0
