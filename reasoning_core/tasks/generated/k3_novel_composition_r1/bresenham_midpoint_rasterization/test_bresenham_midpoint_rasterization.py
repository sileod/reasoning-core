import random

from reasoning_core.tasks.generated.k3_novel_composition_r1.bresenham_midpoint_rasterization.bresenham_midpoint_rasterization import (
    BresenhamMidpointRasterization,
    midpoint_points,
    score_answer,
)


def test_gold_scores_one():
    t = BresenhamMidpointRasterization()
    for _ in range(20):
        entry = t.generate_example()
        assert t.score_answer(entry.answer, entry) == 1.0


def test_answer_in_prompt_domain():
    t = BresenhamMidpointRasterization()
    for _ in range(20):
        entry = t.generate_example()
        pts = entry.metadata["points"]
        assert all(0 <= x <= t.config.max_coord for x, y in pts)
        assert all(0 <= y <= t.config.max_coord for x, y in pts)
        x0, y0 = pts[0]
        x1, y1 = pts[-1]
        assert (x0, y0) != (x1, y1)
        # each consecutive step moves by the line slope plus/minus one
        assert len(pts) >= 2


def test_score_rejects_junk():
    t = BresenhamMidpointRasterization()
    entry = t.generate_example()
    assert score_answer("", entry) == 0.0
    assert score_answer("junk", entry) == 0.0
    assert score_answer("(1,2)", entry) == 0.0


def test_midpoint_rule_adjacency():
    # consecutive points must differ by a unit move (king-neighbor but axis-aligned)
    for _ in range(30):
        t = BresenhamMidpointRasterization()
        entry = t.generate_example()
        pts = entry.metadata["points"]
        for a, b in zip(pts, pts[1:]):
            da, db = abs(a[0] - b[0]), abs(a[1] - b[1])
            assert (da == 1 and db == 0) or (da == 0 and db == 1) or (da == 1 and db == 1)


def test_deterministic_under_seed():
    random.seed(12345)
    t = BresenhamMidpointRasterization()
    e1 = t.generate_example()
    random.seed(12345)
    t2 = BresenhamMidpointRasterization()
    e2 = t2.generate_example()
    assert e1.answer == e2.answer
    assert e1.metadata["points"] == e2.metadata["points"]


def test_endpoints_reached_by_algorithm():
    # small known segments
    assert midpoint_points(0, 0, 5, 2) == [(0, 0), (1, 0), (2, 1), (3, 1), (4, 2), (5, 2)]
    assert midpoint_points(0, 0, 2, 2) == [(0, 0), (1, 1), (2, 2)]
    assert midpoint_points(0, 0, 0, 3) == [(0, 0), (0, 1), (0, 2), (0, 3)]
