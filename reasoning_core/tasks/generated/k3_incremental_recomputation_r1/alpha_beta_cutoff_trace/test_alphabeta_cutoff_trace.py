import random

import pytest

from reasoning_core.tasks.generated.k3_incremental_recomputation_r1.alphabeta_cutoff_trace.alphabeta_cutoff_trace import (
    AlphaBetaConfig,
    AlphaBetaCutoffTraceV2,
    _parse_tree_string,
    _alphabeta_trace,
    _serialize,
)


def test_generate_example_roundtrip():
    task = AlphaBetaCutoffTraceV2()
    for level in (0, 1, 2, 6):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            # gold scores 1
            assert task.score_answer(x.answer, x) == 1.0
            # prompt mentions the tree
            assert x.metadata["tree"] in x.prompt
            # root value within domain
            assert task.config.min_val <= x.metadata["root_value"] <= task.config.max_val


def test_score_answer_garbage():
    task = AlphaBetaCutoffTraceV2()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer(None, x) == 0.0
    assert task.score_answer("0;", x) == 0.0


def test_parser_roundtrip():
    for tree in ("(5,(3,7),2)", "((1,2),3)", "(1,2,3,4)", "(((9)))", "(0,(-1,5))"):
        parsed = _parse_tree_string(tree)
        assert _serialize(parsed) == tree


def test_alphabeta_known_tree():
    # (5,(3,7),2): MAX root. children: 5, (3,7) MIN, 2.
    # alpha=-inf,beta=inf. first child 5 -> value=5, alpha=5.
    # second child MIN(3,7): evaluate 3 cv=3 value=3; 3>? no cutoff (value<=alpha? 3<=5 yes) -> break, prunes 7.
    # returns 3. value stays 5 (3<5). third child 2.
    # root value 5; pruned leaves {7}.
    root = _parse_tree_string("(5,(3,7),2)")
    val, pruned = _alphabeta_trace(root, True)
    assert val == 5
    assert pruned == [7]


def test_alphabeta_no_prune():
    root = _parse_tree_string("((1,2),(3,4))")
    val, pruned = _alphabeta_trace(root, True)
    # MAX root over MIN subtrees. left MIN(1,2): evaluate1 value1; 1<=? no cutoff; eval2 value stays1; 1<=alpha(-inf)? no. returns1 alpha->1.
    # right MIN(3,4): eval3 value3; 3<=alpha1? no; eval4 value stays3; returns3. value->3.
    assert val == 3
    assert pruned == []


def _bruteforce_minimax(node, maximizing):
    """Pure minimax without pruning, leaf->up. Returns the node's value."""
    if isinstance(node, int):
        return node
    if maximizing:
        return max(_bruteforce_minimax(c, False) for c in node)
    else:
        return min(_bruteforce_minimax(c, True) for c in node)


def _all_leaves(node):
    if isinstance(node, int):
        return [node]
    acc = []
    for c in node:
        acc.extend(_all_leaves(c))
    return acc


def test_root_value_equals_pure_minimax():
    task = AlphaBetaCutoffTraceV2()
    for level in (0, 2, 6):
        task.config.set_level(level)
        for _ in range(50):
            x = task.generate_example()
            root = _parse_tree_string(x.metadata["tree"])
            assert _bruteforce_minimax(root, True) == x.metadata["root_value"]


def test_pruned_leaves_are_actual_leaves():
    task = AlphaBetaCutoffTraceV2()
    for _ in range(50):
        task.config.set_level(6)
        x = task.generate_example()
        root = _parse_tree_string(x.metadata["tree"])
        leaves = _all_leaves(root)
        for v in x.metadata["pruned_leaves"]:
            assert leaves.count(v) >= 1
        # answer encodes root;sorted pruned
        assert x.answer == f"{x.metadata['root_value']};" + ",".join(
            str(v) for v in x.metadata["pruned_leaves"]
        )

