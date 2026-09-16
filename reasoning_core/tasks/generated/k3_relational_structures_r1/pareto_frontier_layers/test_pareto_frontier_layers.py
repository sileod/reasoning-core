import random

import pytest

from reasoning_core.tasks.generated.k3_relational_structures_r1.pareto_frontier_layers.pareto_frontier_layers import (
    ParetoFrontierLayers,
    _dom_counts,
    _pair_labels,
    _pareto_layers,
    _sorted_pareto_fronts,
)


def test_generate_all_modes_and_score():
    random.seed(1)
    task = ParetoFrontierLayers()
    modes_seen = set()
    for _ in range(200):
        e = task.generate_example()
        modes_seen.add(e.metadata["mode"])
        assert task.score_answer(e.answer, e) == 1.0
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("x y z junk", e) == 0.0
    assert modes_seen == {"layers", "kfront", "counts", "pairs"}


def test_levels():
    task = ParetoFrontierLayers()
    for level in range(0, 7):
        task.config.set_level(level)
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_helpers():
    pts = [[1, 3], [3, 1], [2, 2], [5, 5]]
    mx = [True, True]
    assert _pareto_layers(pts, mx) == [2, 2, 2, 1]
    assert _sorted_pareto_fronts(pts, mx) == [[3], [0, 1, 2]]
    assert _dom_counts(pts, mx) == [1, 1, 1, 0]


def test_pair_labels_equal():
    pts = [[2, 2], [2, 2]]
    assert _pair_labels(pts, [True, True], [(0, 1)]) == ["E"]


def test_dedup_stable():
    task = ParetoFrontierLayers()
    a = task.generate_example()
    assert isinstance(a.deduplication_key, str) and len(a.deduplication_key) > 0
