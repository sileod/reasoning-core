import random

import pytest

from reasoning_core.template import Task
from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.hyperedge_replacement_derivation.hyperedge_replacement_derivation import (
    HyperedgeReplacementDerivation,
    _canonical_str,
    _derive,
    _parse_edges,
)


def test_gold_scores_one():
    task = HyperedgeReplacementDerivation()
    for level in (0, 2, 5):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    task = HyperedgeReplacementDerivation()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("(1,2,x)", entry) == 0.0
    assert task.score_answer("garbage!!", entry) == 0.0


def test_order_independent_scoring():
    task = HyperedgeReplacementDerivation()
    entry = task.generate_example()
    edges = _parse_edges(entry.answer)
    reordered = ";".join("(%d,%d,%s)" % e for e in reversed(edges))
    assert task.score_answer(reordered, entry) == 1.0


def test_canonical_is_sorted_and_survives_roundtrip():
    edges = [(2, 1, "x"), (5, 3, "y"), (1, 2, "x")]
    s = _canonical_str(edges)
    assert s == "(1,2,x);(2,1,x);(5,3,y)"
    assert _parse_edges(s) == sorted(((1, 2, "x"), (2, 1, "x"), (5, 3, "y")))


def test_difficulty_changes_config():
    task = HyperedgeReplacementDerivation()
    base = task.config.num_nt
    task.config.set_level(5)
    assert task.config.num_nt > base


def test_generation_survives_all_levels():
    task = HyperedgeReplacementDerivation()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        nums = [n for (s, t, l) in _parse_edges(entry.answer)
                for n in (s, t)]
        assert all(n >= 1 for n in nums)


def test_arity_matches_boundary_references():
    task = HyperedgeReplacementDerivation()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        ar = entry.metadata["arity"]
        for b, i, edges in entry.metadata["productions"]:
            assert len(b) == ar


def test_answer_domain_and_derivation_consistency():
    task = HyperedgeReplacementDerivation()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        nv = entry.metadata["nv"]
        edges = _parse_edges(entry.answer)
        for s, t, l in edges:
            assert s >= 1 and t >= 1
            assert l in ("x", "y", "z")
        # Every nonterminal was addressed; no A edges survive in the final list.
        assert all(len(tok) == 3 and tok[2] in ("x", "y", "z") for tok in edges)


def test_no_constant_answer_within_level():
    random.seed(12345)
    task = HyperedgeReplacementDerivation()
    for level in (0, 2, 5):
        task.config.set_level(level)
        answers = {task.generate_example().answer for _ in range(20)}
        assert len(answers) >= 5


def test_multiple_levels_change_answer_complexity():
    random.seed(99)
    task = HyperedgeReplacementDerivation()
    task.config.set_level(0)
    small = len(_parse_edges(task.generate_example().answer))
    task.config.set_level(6)
    big = len(_parse_edges(task.generate_example().answer))
    assert big > small
