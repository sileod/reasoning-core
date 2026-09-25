import random

from reasoning_core.tasks.generated.ua_representation_transfer_r4.loom_shed_memory.loom_shed_memory import (
    LoomShedMemory, LoomShedMemoryV2Config, _simulate, _count_floats, _cross_order,
)

random.seed(2302342651)


def _make(level=0):
    task = LoomShedMemory()
    cfg = LoomShedMemoryV2Config()
    cfg.set_level(level)
    task.config = cfg
    return task


def test_generate_and_score():
    task = _make(2)
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = _make(2)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("nonsense", ex) == 0.0
    assert task.score_answer("1.5", ex) == 0.0


def test_difficulty_changes():
    cfg = LoomShedMemoryV2Config()
    cfg.set_level(0)
    base = cfg.n_picks
    cfg.set_level(5)
    assert cfg.n_picks >= base
    assert cfg.n_warps >= 5


def test_levels_generate():
    task = LoomShedMemory()
    for level in [0, 1, 2, 3, 5, 6]:
        cfg = LoomShedMemoryV2Config()
        cfg.set_level(level)
        task.config = cfg
        seen = set()
        for _ in range(8):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.answer)
        assert len(seen) >= 2


def test_answer_is_nonnegative():
    task = _make(3)
    for _ in range(20):
        ex = task.generate_example()
        assert int(ex.answer) >= 0


def test_helpers_agree():
    sheds = [frozenset({0}), frozenset(), frozenset(), frozenset()]
    threading = [0]
    crossing = _cross_order(4, None)
    assert _count_floats(sheds, threading, crossing, 1) == 1
    ops = [("press", 0), ("hold", ()), ("release", (0,))]
    assert _simulate(ops, [(0,)]) == [frozenset({0}), frozenset({0}), frozenset()]
