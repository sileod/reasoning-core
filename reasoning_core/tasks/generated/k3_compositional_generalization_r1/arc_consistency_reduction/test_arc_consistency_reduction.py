import pytest

from reasoning_core.tasks.generated.k3_compositional_generalization_r1.arc_consistency_reduction.arc_consistency_reduction import (
    ArcConsistencyReduction,
)


def test_generate_render_score_roundtrip():
    task = ArcConsistencyReduction()
    for _ in range(50):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        assert entry.metadata["answer_kind"] in ("domains", "wipeout")
        assert task.score_answer(entry.answer, entry) == 1.0


def test_random_answers_do_not_score_one():
    task = ArcConsistencyReduction()
    for _ in range(30):
        entry = task.generate_example()
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("garbage", entry) == 0.0
        if entry.metadata["answer_kind"] == "domains":
            assert task.score_answer("x", entry) == 0.0
        else:
            assert task.score_answer("0,1|2", entry) == 0.0


def test_difficulty_scaling():
    task = ArcConsistencyReduction()
    l0 = task.config.num_vars
    task.config.set_level(5)
    l5 = task.config.num_vars
    assert l5 > l0


def test_all_levels_generate():
    task = ArcConsistencyReduction()
    for level in range(0, 7):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
