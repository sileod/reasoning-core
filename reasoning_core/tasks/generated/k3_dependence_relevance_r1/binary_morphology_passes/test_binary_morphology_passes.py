import random

from reasoning_core.tasks.generated.k3_dependence_relevance_r1.binary_morphology_passes.binary_morphology_passes import (
    BinaryMorphologyPasses,
    _erode,
    _dilate,
    _openclose,
    _hitmiss,
    _SE,
    _HM,
)


def test_erode_box_cross():
    grid = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ]
    se = _SE["cross"]["offsets"]
    out = _erode(grid, se)
    assert out[1][1] == 1
    center = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    assert sum(sum(r) for r in _erode(center, se)) == 0


def test_dilate_cross_grows():
    grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    se = _SE["cross"]["offsets"]
    out = _dilate(grid, se)
    assert sum(sum(r) for r in out) == 5


def test_open_close_idempotent_cross():
    se = _SE["cross"]["offsets"]
    grid = [[1, 1, 1, 1, 1] for _ in range(5)]
    opened = _openclose(grid, "open", se)
    assert _openclose(opened, "open", se) == opened
    closed = _openclose(grid, "close", se)
    assert _openclose(closed, "close", se) == closed


def test_hitmiss_corner():
    grid = [
        [1, 1, 0],
        [1, 0, 0],
        [0, 0, 0],
    ]
    out = _hitmiss(grid, _HM["corner"])
    assert sum(sum(r) for r in out) == 1


def test_roundtrip_and_score():
    task = BinaryMorphologyPasses()
    for _ in range(30):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1
        assert 0 < int(entry.answer) < entry.metadata.h * entry.metadata.w


def test_difficulty_changes():
    task = BinaryMorphologyPasses()
    cfg = type(task.config)()
    cfg.set_level(0)
    base = (cfg.grid_size, cfg.n_passes)
    cfg.set_level(6)
    high = (cfg.grid_size, cfg.n_passes)
    assert high[0] >= base[0] and high[1] >= base[1]


def test_generation_all_levels():
    for level in range(7):
        task = BinaryMorphologyPasses()
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1
