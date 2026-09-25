import itertools
import random

from reasoning_core.tasks.generated.ua_hierarchical_recursive_r4.hierarchical_quorum_overlap.hierarchical_quorum_overlap import (
    HierarchicalQuorumOverlap, HierarchicalQuorumOverlapConfig,
    _build_tree, _leaf_set, _satisfied, _solve, _mincost, _parse_answer,
)


def _brute_force(tree_a, tree_b):
    leaves = sorted(_leaf_set(tree_a) | _leaf_set(tree_b))
    best = None
    best_set = None
    for mask in range(1 << len(leaves)):
        sel = {leaves[i] for i in range(len(leaves)) if (mask >> i) & 1}
        if _satisfied(tree_a, sel) and _satisfied(tree_b, sel):
            if best is None or len(sel) < best:
                best = len(sel)
                best_set = sorted(sel)
    return best, best_set


def _make_instance(members_a, members_b, depth_a, depth_b, shared_total):
    shared_pool = ['sx', 'sy', 'sz', 'sw', 'sv', 'su'][:shared_total]
    overlap = random.randint(0, shared_total)
    core = random.sample(shared_pool, overlap)
    rest = [s for s in shared_pool if s not in core]
    use_a = core + random.sample(rest, random.randint(0, len(rest)))
    use_b = core + random.sample(rest, random.randint(0, len(rest)))
    priv_a = list('abcdefghij')[:members_a]
    priv_b = list('klmnopqrst')[:members_b]
    tree_a = _build_tree(use_a + priv_a, depth_a)
    tree_b = _build_tree(use_b + priv_b, depth_b)
    return tree_a, tree_b


def test_mincost_leaf():
    assert _mincost('a', set(), set()) == (1, frozenset(['a']))
    assert _mincost('a', {'a'}, {'a'}) == (0, frozenset(['a']))


def test_satisfied_simple():
    tree = [0.5, 'a', 'b', 'c']
    assert not _satisfied(tree, {'a'})
    assert _satisfied(tree, {'a', 'b'})
    assert not _satisfied(tree, set())


def test_solve_matches_bruteforce_random():
    random.seed(7)
    for _ in range(40):
        tree_a, tree_b = _make_instance(
            random.randint(1, 3), random.randint(1, 3),
            random.randint(1, 2), random.randint(1, 2),
            random.randint(0, 2),
        )
        res = _solve(tree_a, tree_b)
        if res is None:
            continue
        k, common = res
        bf_k, bf_set = _brute_force(tree_a, tree_b)
        assert k == bf_k
        assert len(common) == k
        assert _satisfied(tree_a, set(common)) and _satisfied(tree_b, set(common))


def test_gold_scores_one_all_levels():
    random.seed(11)
    t = HierarchicalQuorumOverlap()
    for level in range(7):
        cfg = HierarchicalQuorumOverlapConfig()
        cfg.set_level(level)
        t.config = cfg
        for _ in range(20):
            e = t.generate_entry()
            assert e.metadata.min_size >= 1
            assert t.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    random.seed(13)
    t = HierarchicalQuorumOverlap()
    for _ in range(20):
        e = t.generate_entry()
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("random garbage", e) == 0.0
        assert t.score_answer("10 | [1,2] | [1,2]", e) == 0.0
        assert t.score_answer("foo | x | y", e) == 0.0


def test_wrong_cardinality_scores_zero():
    random.seed(17)
    t = HierarchicalQuorumOverlap()
    for _ in range(20):
        e = t.generate_entry()
        k = e.metadata.min_size
        common = e.metadata.common
        wrong = str(k + 1) + " | " + str(common) + " | " + str(common)
        assert t.score_answer(wrong, e) == 0.0


def test_deterministic_under_seed():
    random.seed(99)
    t = HierarchicalQuorumOverlap()
    e1 = t.generate_entry()
    random.seed(99)
    t2 = HierarchicalQuorumOverlap()
    e2 = t2.generate_entry()
    assert e1.answer == e2.answer
    assert e1.metadata.tree_a == e2.metadata.tree_a
    assert e1.metadata.tree_b == e2.metadata.tree_b


def test_parse_answer():
    assert _parse_answer("2 | ['sx', 'a'] | ['sx', 'a']") == (2, ['sx', 'a'], ['sx', 'a'])
    assert _parse_answer("garbage") is None
    assert _parse_answer("3 | [1, 2] | [1, 2]") is None
    assert _parse_answer("x | ['a'] | ['a']") is None
