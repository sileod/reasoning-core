import random

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.quadtree_region_construction.quadtree_region_construction import (
    QuadtreeRegionConstruction,
)


def test_difficulty_changes():
    t = QuadtreeRegionConstruction()
    base = QuadtreeRegionConstruction.config_cls()
    t.config.set_level(0)
    c0 = base.min_size
    t.config.set_level(6)
    assert t.config.max_size >= c0


def test_gold_roundtrip_scores():
    t = QuadtreeRegionConstruction()
    for level in (0, 2, 5, 6):
        t.config.set_level(level)
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_wrong_answer_scores_zero():
    t = QuadtreeRegionConstruction()
    t.config.set_level(0)
    e = t.generate_example()
    assert t.score_answer("", e) == 0.0
    assert t.score_answer("junk", e) == 0.0


def test_grid_varied():
    t = QuadtreeRegionConstruction()
    ans = set()
    for _ in range(50):
        t.config.set_level(0)
        e = t.generate_example()
        ans.add(e.answer)
    assert len(ans) > 1


def test_validation():
    t = QuadtreeRegionConstruction()
    t.validate()
