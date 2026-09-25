import random

import pytest

from reasoning_core.tasks.generated.ua_planning_backtracking_r5.common_polyhedral_net.common_polyhedral_net import (
    CommonPolyhedralNet,
    valid_net,
    _TREES,
)


def test_valid_cube_cross_net():
    tree = ((0, 2), (0, 3), (0, 4), (0, 5), (1, 2))
    assert valid_net((1, 1, 1), tree)


def test_trees_nonempty():
    assert len(_TREES) >= 11


def test_gold_scores_one():
    task = CommonPolyhedralNet()
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = CommonPolyhedralNet()
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("garbage", ex) < 1.0


def test_both_labels_all_levels():
    for level in (0, 2, 5):
        task = CommonPolyhedralNet()
        task.config.set_level(level)
        seen = set()
        for _ in range(60):
            ex = task.generate_example()
            seen.add(ex.metadata["possible"])
        assert seen == {True, False}


def test_label_balance_ok():
    task = CommonPolyhedralNet()
    yes = 0
    n = 120
    for _ in range(n):
        ex = task.generate_example()
        if ex.metadata["possible"]:
            yes += 1
    p = yes / n
    assert 0.3 <= p <= 0.7


def test_deterministic_generation():
    random.seed(3)
    a = CommonPolyhedralNet().generate_example()
    random.seed(3)
    b = CommonPolyhedralNet().generate_example()
    assert a.answer == b.answer
    assert a.metadata["possible"] == b.metadata["possible"]
    assert a.metadata["specs"] == b.metadata["specs"]


def test_validate():
    CommonPolyhedralNet().validate()
