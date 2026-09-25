import random

import pytest

from reasoning_core.tasks.generated.ua_formal_logic_r5.team_semantics_evaluation import (
    team_semantics_evaluation as mod,
)

T = mod.TeamSemanticsEvaluation


def test_generate_and_score_all_levels():
    task = T()
    for level in range(7):
        task.config.set_level(level)
        seen = set()
        for _ in range(20):
            ex = task.generate_example()
            assert ex.prompt
            assert task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.answer)
        assert seen == {"Yes", "No"}, f"level {level} not balanced: {seen}"


def test_junk_answers_score_zero():
    task = T()
    task.config.set_level(0)
    ex = task.generate_example()
    for junk in ["", "import fakemodule", "maybe", "7", "1", "yesyes"]:
        assert task.score_answer(junk, ex) == 0.0


def test_dedup_key_stable():
    task = T()
    task.config.set_level(2)
    ex = task.generate_example()
    key1 = task.deduplication_key(ex)
    ex2 = task.generate_example()
    assert isinstance(key1, str)


def test_seed_reproducible():
    random.seed(12345)
    a = [T().generate_example().answer for _ in range(30)]
    random.seed(12345)
    b = [T().generate_example().answer for _ in range(30)]
    assert a == b
