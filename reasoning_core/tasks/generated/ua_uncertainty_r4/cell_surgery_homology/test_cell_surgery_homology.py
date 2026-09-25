import random

from reasoning_core.tasks.generated.ua_uncertainty_r4.cell_surgery_homology.cell_surgery_homology import (
    CellSurgeryHomology,
    _homology,
    _render_grid,
)


def _make():
    return CellSurgeryHomology()


def test_generate_and_render_and_score():
    random.seed(0)
    t = _make()
    for _ in range(60):
        e = t.generate_example()
        assert e.answer.count(" ") == 2
        parts = [int(p) for p in e.answer.split()]
        assert len(parts) == 3 and all(p >= 0 for p in parts)
        assert parts[2] == 0
        assert t.score_answer(e.answer, e) == 1.0
        prompt = t.render_prompt(e.metadata)
        assert "BEFORE any surgical change" in prompt


def test_junk_scores_zero():
    random.seed(1)
    t = _make()
    e = t.generate_example()
    assert t.score_answer("", e) == 0.0
    assert t.score_answer("not an answer", e) == 0.0
    assert t.score_answer("1 2", e) == 0.0
    assert t.score_answer("1 2 3 4", e) == 0.0


def test_all_levels_generate():
    random.seed(2)
    for level in range(7):
        t = CellSurgeryHomology()
        e = t.generate_example(level=level)
        assert t.score_answer(e.answer, e) == 1.0


def test_ring_has_one_hole():
    ring = set()
    for x in range(3):
        for y in range(3):
            if x in (0, 2) or y in (0, 2):
                ring.add((x, y))
    b0, b1, b2 = _homology(ring)
    assert (b0, b1, b2) == (1, 1, 0)
