from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.redundant_signal_race_bounds.redundant_signal_race_bounds import (
    RedundantSignalRaceBounds,
    feasible_interval,
    _parse_interval,
)


def test_gold_scores():
    task = RedundantSignalRaceBounds()
    for _ in range(40):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_garbage_scores_zero():
    task = RedundantSignalRaceBounds()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0
    assert task.score_answer("12", entry) == 0.0
    assert task.score_answer("0.5, 0.9", entry) == 0.0


def test_interval_domain():
    task = RedundantSignalRaceBounds()
    for _ in range(60):
        entry = task.generate_example()
        md = entry["metadata"]
        assert 0.0 <= md["lo"] <= md["hi"] <= 1.0


def test_frechet_bounds():
    channels = [(0.4, 2, 3), (0.2, 3, 2), (0.0, 2, 1)]
    lo, hi = feasible_interval(channels)
    assert abs(lo - 0.4 / 3) < 1e-6
    assert abs(hi - 0.4) < 1e-6


def test_levels_change_config():
    task = RedundantSignalRaceBounds()
    c0 = RedundantSignalRaceBounds.config_cls(level=0)
    c6 = RedundantSignalRaceBounds.config_cls(level=6)
    task.config.set_level(0)
    task.config.set_level(6)
    assert c6.n_channels >= c0.n_channels


def test_parse_interval():
    assert _parse_interval("[0.12, 0.85]") == (0.12, 0.85)
    assert _parse_interval("[0, 1]") == (0.0, 1.0)
    assert _parse_interval("0.12, 0.85") is None
    assert _parse_interval("[abc]") is None
