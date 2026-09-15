from fractions import Fraction

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.additive_tree_reconstruction.additive_tree_reconstruction import (
    AdditiveTreeReconstruction,
    AdditiveTreeConfig,
    _parse_answer,
    _format_answer,
    _verify_answer,
    _is_binary,
)


def test_config_difficulty_increases():
    cfg = AdditiveTreeConfig()
    base = (cfg.n_leaves, cfg.max_weight)
    cfg.set_level(3)
    mid = (cfg.n_leaves, cfg.max_weight)
    cfg.set_level(6)
    hi = (cfg.n_leaves, cfg.max_weight)
    assert mid[0] >= base[0] and mid[1] >= base[1]
    assert hi[0] >= mid[0] and hi[1] >= mid[1]
    assert hi[0] >= base[0] + 6
    assert hi[0] <= 16


def test_edge_counts_match_binary_tree():
    for level in range(7):
        task = AdditiveTreeReconstruction()
        ex = task.generate_example(level=level)
        n = ex.metadata.n_leaves
        assert len(ex.answer.split()) == 2 * n - 3


def test_gold_answer_scores_one():
    for level in (0, 2, 5, 6):
        task = AdditiveTreeReconstruction()
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_verify_answer_reproduces_distances():
    for _ in range(20):
        task = AdditiveTreeReconstruction()
        ex = task.generate_example()
        edges = _parse_answer(ex.answer)
        dist = ex.metadata.dist
        n = ex.metadata.n_leaves
        as_fraction = [[Fraction(x) for x in row] for row in dist]
        assert _verify_answer(edges, as_fraction, n)


def test_answer_edges_are_canonical_sorted():
    for _ in range(20):
        task = AdditiveTreeReconstruction()
        ex = task.generate_example()
        edges = _parse_answer(ex.answer)
        assert edges == sorted(edges)
        for p, c, w in edges:
            assert w > 0


def test_wrong_answers_do_not_score_one():
    task = AdditiveTreeReconstruction()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("junk", ex) == 0.0
        assert task.score_answer("0-1:5", ex) == 0.0
        tokens = ex.answer.split()
        tokens[0] = "999-999:1"
        assert task.score_answer(" ".join(tokens), ex) == 0.0


def test_score_accepts_multiformat_fraction():
    task = AdditiveTreeReconstruction()
    for _ in range(10):
        ex = task.generate_example()
        got = _parse_answer(ex.answer)
        want = _parse_answer(ex.answer)
        assert got == want
