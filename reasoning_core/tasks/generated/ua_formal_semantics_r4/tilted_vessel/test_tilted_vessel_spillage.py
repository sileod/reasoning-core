import random

from reasoning_core.tasks.generated.ua_formal_semantics_r4.tilted_vessel.tilted_vessel_spillage import (
    TiltedVessel,
    _area,
    _cap,
    _clip_y,
    _rotate,
)


def test_gold_scores_correct():
    task = TiltedVessel()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_oneg_per_level():
    task = TiltedVessel()
    for level in (0, 2, 5):
        task.config.set_level(level)
        answers = set()
        for _ in range(30):
            answers.add(task.generate_example().answer)
        assert len(answers) > 1, f"level {level} degenerated to a single answer"


def test_junk_not_scored():
    task = TiltedVessel()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("reajrjrje9595!", ex) < 1.0
    assert task.score_answer("12.0.9", ex) < 1.0


def test_retained_domain():
    task = TiltedVessel()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            assert ex.metadata["retained"] >= 0


def test_helpers_are_exact_on_flat_basin():
    poly = [(0, 10), (0, 2), (10, 2), (10, 10), (0, 10)]
    assert abs(_area(poly) - 80.0) < 1e-9
    assert abs(_area(_clip_y(poly, 10)) - 80.0) < 1e-9
    assert abs(_cap(poly) - 80.0) < 1e-9
