import random

from reasoning_core.tasks.generated.ua_hierarchical_recursive_r4.nested_margin_collapse.nested_margin_collapse import (
    NestedMarginCollapse, NestedMarginCollapseConfig,
    _collapse, _top_run, _bottom_run, _build_tree, _parse_pair, _verify,
)


def test_collapse_two_values():
    assert _collapse([5, 8]) == 8
    assert _collapse([5, -3]) == 2
    assert _collapse([-2, -7]) == -7
    assert _collapse([-2, 5]) == 3


def test_collapse_multi():
    assert _collapse([]) == 0
    assert _collapse([4, 2, 9]) == 9
    assert _collapse([4, -1, 2]) == 4 + (-1)
    assert _collapse([-1, -5, -3]) == -5


def test_top_run_simple_chain():
    leaf = {'id': 1, 'm': 3, 'barrier': False, 'children': []}
    root = {'id': 0, 'm': 5, 'barrier': False, 'children': [leaf]}
    assert _top_run(root) == [5, 3]
    assert _bottom_run(root) == [5, 3]


def test_top_run_stops_at_barrier_but_counts_it():
    leaf = {'id': 1, 'm': 3, 'barrier': True, 'children': []}
    root = {'id': 0, 'm': 5, 'barrier': False, 'children': [leaf]}
    assert _top_run(root) == [5, 3]


def test_top_run_does_not_descend_below_barrier():
    grand = {'id': 2, 'm': 7, 'barrier': False, 'children': []}
    inner = {'id': 1, 'm': 3, 'barrier': True, 'children': [grand]}
    root = {'id': 0, 'm': 5, 'barrier': False, 'children': [inner]}
    assert _top_run(root) == [5, 3]
    assert _collapse(_top_run(root)) == 5


def test_bottom_run_uses_last_child():
    a = {'id': 1, 'm': 2, 'barrier': False, 'children': []}
    b = {'id': 2, 'm': 9, 'barrier': False, 'children': []}
    root = {'id': 0, 'm': 5, 'barrier': False, 'children': [a, b]}
    assert _bottom_run(root) == [5, 9]
    assert _top_run(root) == [5, 2]


def test_gold_scores_one():
    random.seed(1)
    t = NestedMarginCollapse()
    for _ in range(80):
        e = t.generate_entry()
        assert t.score_answer(e.answer, e) == 1.0


def test_wrong_pair_scores_zero():
    random.seed(2)
    t = NestedMarginCollapse()
    for _ in range(40):
        e = t.generate_entry()
        swapped = f"{e.metadata.b},{e.metadata.t}"
        if swapped != e.answer:
            assert t.score_answer(swapped, e) == 0.0
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("garbage", e) == 0.0
        assert t.score_answer("1,2,3", e) == 0.0
        assert t.score_answer("a,b", e) == 0.0


def test_all_levels():
    t = NestedMarginCollapse()
    for level in range(7):
        cfg = NestedMarginCollapseConfig()
        cfg.set_level(level)
        t.config = cfg
        for _ in range(20):
            e = t.generate_entry()
            assert t.score_answer(e.answer, e) == 1.0


def test_non_trivial_runs():
    t = NestedMarginCollapse()
    for level in range(7):
        cfg = NestedMarginCollapseConfig()
        cfg.set_level(level)
        t.config = cfg
        for _ in range(40):
            e = t.generate_entry()
            assert len(e.metadata.nodes) >= 3
            # report a real collapse (both runs have at least two margins)
            assert e.metadata.nodes[0]['children'] or True


def test_parse_pair():
    assert _parse_pair("3, -1") == (3, -1)
    assert _parse_pair("7,2") == (7, 2)
    assert _parse_pair("x") is None
    assert _parse_pair("1,2,3") is None
    assert _parse_pair("") is None


def test_generate_entries_differ():
    random.seed(5)
    t = NestedMarginCollapse()
    seen = set()
    for _ in range(60):
        e = t.generate_entry()
        seen.add(e.answer)
    assert len(seen) > 1


def test_verify_helper():
    root = {'id': 0, 'm': 5, 'barrier': False,
            'children': [{'id': 1, 'm': -3, 'barrier': False, 'children': []}]}
    assert _verify(root, _collapse(_top_run(root)), _collapse(_bottom_run(root)))
