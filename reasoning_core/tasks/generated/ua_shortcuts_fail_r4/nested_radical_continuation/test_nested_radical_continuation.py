import random

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.nested_radical_continuation import (
    nested_radical_continuation as m,
)


def _make(level, seed=0):
    t = m.NestedRadicalContinuation()
    t.config.set_level(level)
    return t


def test_generates_and_scores_gold():
    for level in range(7):
        t = _make(level)
        for _ in range(10):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_wrong_and_junk_rejected():
    t = _make(2)
    ex = t.generate_example()
    assert t.score_answer("", ex) < 1.0
    assert t.score_answer("0, 0", ex) < 1.0
    assert t.score_answer("999", ex) < 1.0


def test_normalization_tolerates_spacing():
    t = _make(3)
    ex = t.generate_example()
    gold = " ".join(ex.answer.split())
    no_space = gold.replace(", ", ",")
    assert t.score_answer(no_space, ex) == 1.0
    assert t.score_answer(gold, ex) == 1.0


def test_difficulty_changes_config():
    t0 = _make(0)
    t6 = _make(6)
    assert t0.config.num_points < t6.config.num_points
    assert t0.config.turns < t6.config.turns


def test_winding_matches_explicit_square():
    square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    assert m._winding(square, 1, 1) == 1
    assert m._winding(square, 5, 5) == 0
    cw = [(0, 0), (0, 3), (3, 3), (3, 0)]
    assert m._winding(cw, 1, 1) == -1


def test_all_levels_produce_answers():
    for level in range(7):
        t = _make(level, seed=7)
        ex = t.generate_example()
        w = [int(x) for x in ex.answer.split(",")]
        assert len(w) == len(ex.metadata["branch_points"])
        assert w == ex.metadata["windings"]


def test_avoidance_and_offset_consistent():
    random.seed(11)
    for level in range(7):
        t = _make(level)
        cfg = t.config
        verts, pts, windings = m._gen_instance(cfg.num_points, cfg.turns, cfg.max_step)
        assert all(p not in {tuple(v) for v in verts} for p in pts)
