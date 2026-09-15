import random

from reasoning_core.tasks.generated.wave12.pragmatic_reference_generation.pragmatic_reference_generation import (
    PragmaticReferenceGeneration,
    score_scalar,
)


def _make(level):
    task = PragmaticReferenceGeneration()
    task.config.set_level(level)
    return task


def test_gold_scores_one():
    for level in range(7):
        task = _make(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_scores_zero():
    task = _make(3)
    ex = task.generate_example()
    assert task.score_answer("red square right", ex) < 1.0
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer(5, ex) < 1.0


def test_answer_is_in_scene():
    task = _make(5)
    ex = task.generate_example()
    assert ex.answer in ex.metadata["scene"]


def test_distractors_share_attribute():
    task = _make(2)
    for _ in range(30):
        ex = task.generate_example()
        target_color, target_shape, _ = ex.answer.split()
        for other in ex.metadata["scene"]:
            if other == ex.answer:
                continue
            c, s, _ = other.split()
            assert (c == target_color) or (s == target_shape)


def test_clue_unique():
    task = _make(4)
    for _ in range(30):
        ex = task.generate_example()
        c, s = ex.metadata["clue"].split()
        matches = [o for o in ex.metadata["scene"] if o.startswith(f"{c} {s}")]
        assert len(matches) == 1
        assert matches[0] == ex.answer


def test_levels_differ():
    cfg0 = _make(0).config
    cfg6 = _make(6).config
    assert cfg6.n_distractors > cfg0.n_distractors


def test_no_constant_answer_across_levels():
    answers = set()
    for level in range(7):
        task = _make(level)
        for _ in range(50):
            answers.add(task.generate_example().answer)
    assert len(answers) >= 7
