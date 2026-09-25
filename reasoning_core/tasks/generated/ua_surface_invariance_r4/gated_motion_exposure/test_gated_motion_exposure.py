import random

random.seed(2302342651)

from reasoning_core.tasks.generated.ua_surface_invariance_r4.gated_motion_exposure.gated_motion_exposure import (
    GatedMotionExposure,
    GatedMotionExposureConfig,
    _inside_any,
    _exposure_for_window,
)


def test_gold_scores_one():
    task = GatedMotionExposure()
    for _ in range(30):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    task = GatedMotionExposure()
    entry = task.generate_example()
    for bad in ["", "abc", "nan", "inf", "None"]:
        assert task.score_answer(bad, entry) == 0.0


def test_output_is_decimal():
    task = GatedMotionExposure()
    for _ in range(10):
        entry = task.generate_example()
        assert entry.answer.count(".") == 1
        val = float(entry.answer)
        assert val >= 0.0
        assert entry.metadata["total"] >= 0.0


def test_path_starts_outside():
    task = GatedMotionExposure()
    for _ in range(100):
        entry = task.generate_example()
        assert not _inside_any(entry.metadata["path"][0], entry.metadata["windows"])


def test_difficulty_changes():
    task = GatedMotionExposure()
    c0 = GatedMotionExposureConfig()
    c0.set_level(0)
    c6 = GatedMotionExposureConfig()
    c6.set_level(6)
    assert c6.n_waypoints > c0.n_waypoints or c6.n_windows > c0.n_windows


def test_exposure_domain():
    task = GatedMotionExposure()
    for _ in range(50):
        entry = task.generate_example()
        period = entry.metadata["period"]
        dwell = entry.metadata["dwell"]
        assert 0 < dwell < period
