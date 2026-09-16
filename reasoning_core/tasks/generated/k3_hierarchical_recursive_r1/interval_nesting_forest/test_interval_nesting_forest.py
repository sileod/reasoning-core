import random

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.interval_nesting_forest.interval_nesting_forest import (
    IntervalNestingForest, IntervalNestingForestConfig,
    _compute_parents, _preorder, _parse_ids,
)


def test_parent_rule():
    intervals = [(0, 10), (2, 12), (5, 6)]
    parents = _compute_parents(intervals)
    assert parents[2] == 0
    assert parents[0] == -1
    assert parents[1] == -1


def test_tie_break_smaller_left():
    intervals = [(0, 12), (3, 15), (6, 7)]
    parents = _compute_parents(intervals)
    assert parents[2] == 0


def test_preorder_valid():
    intervals = [(3, 7), (1, 9), (0, 12)]
    parents = _compute_parents(intervals)
    pre = _preorder(intervals, parents)
    assert sorted(pre) == list(range(3))
    pos = {v: i for i, v in enumerate(pre)}
    for i in range(3):
        if parents[i] != -1:
            assert pos[parents[i]] < pos[i]


def test_gold_scores_one():
    random.seed(1)
    t = IntervalNestingForest()
    for _ in range(50):
        e = t.generate_entry()
        assert t.score_answer(e.answer, e) == 1.0


def test_wrong_order_scores_zero():
    random.seed(2)
    t = IntervalNestingForest()
    for _ in range(30):
        e = t.generate_entry()
        rev = list(reversed(e.metadata.preorder))
        if rev != e.metadata.preorder:
            assert t.score_answer(",".join(str(v) for v in rev), e) == 0.0


def test_junk_scores_zero():
    random.seed(3)
    t = IntervalNestingForest()
    for _ in range(30):
        e = t.generate_entry()
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("random garbage", e) == 0.0
        assert t.score_answer("1,abc,3", e) == 0.0


def test_all_levels():
    t = IntervalNestingForest()
    for level in range(7):
        cfg = IntervalNestingForestConfig()
        cfg.set_level(level)
        t.config = cfg
        for _ in range(20):
            e = t.generate_entry()
            assert t.score_answer(e.answer, e) == 1.0


def test_levels_non_trivial():
    t = IntervalNestingForest()
    for level in range(7):
        cfg = IntervalNestingForestConfig()
        cfg.set_level(level)
        t.config = cfg
        n_root = cfg.n
        non_root_seen = False
        for _ in range(30):
            e = t.generate_entry()
            if any(p != -1 for p in e.metadata.parents):
                non_root_seen = True
                break
        assert non_root_seen


def test_parse_ids():
    assert _parse_ids("3, 1, 0") == [3, 1, 0]
    assert _parse_ids("7") == [7]
    assert _parse_ids("a,b") is None


def test_equal_left_are_siblings():
    # Strict containment requires l_J < l_I, so intervals with equal left
    # endpoints never contain one another -- [1,9], [1,4], [1,6] are siblings.
    intervals = [(1, 9), (1, 4), (1, 6)]
    parents = _compute_parents(intervals)
    assert parents == [-1, -1, -1]
    pre = _preorder(intervals, parents)
    assert pre == [0, 1, 2]


def test_roots_ordered_leftmost():
    # Overlapping siblings that are both roots must be ordered by left endpoint.
    intervals = [(4, 9), (1, 7)]
    parents = _compute_parents(intervals)
    assert parents == [-1, -1]
    pre = _preorder(intervals, parents)
    assert pre == [1, 0]
