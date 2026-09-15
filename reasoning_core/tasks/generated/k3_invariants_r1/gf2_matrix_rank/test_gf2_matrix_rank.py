import random

from reasoning_core.tasks.generated.k3_invariants_r1.gf2_matrix_rank.gf2_matrix_rank import (
    GF2MatrixRank, _pivot_columns, _rank, score_answer,
)


def test_gold_scores_one():
    task = GF2MatrixRank()
    for _ in range(50):
        task.config.set_level(random.randint(0, 6))
        x = task.generate_example()
        assert score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    task = GF2MatrixRank()
    x = task.generate_example()
    assert score_answer('', x) == 0.0
    assert score_answer('abc', x) == 0.0
    assert score_answer(',,,', x) == 0.0
    assert score_answer('0,1,2,999', x) == 0.0


def test_wrong_answer_scores_zero():
    task = GF2MatrixRank()
    task.config.set_level(3)
    x = task.generate_example()
    good = x.answer
    pivs = [int(c) for c in good.split(',')]
    if pivs:
        wrong = list(pivs)
        wrong[0] = (wrong[0] + 1) % (max(pivs) + 3)
        assert score_answer(','.join(str(v) for v in wrong), x) == 0.0


def test_pivot_set_consistent():
    for _ in range(30):
        task = GF2MatrixRank()
        task.config.set_level(random.randint(0, 6))
        x = task.generate_example()
        m = x.metadata['matrix']
        assert len([int(c) for c in x.answer.split(',')]) == _rank(m)
        assert _pivot_columns(m) == [int(c) for c in x.answer.split(',')]


def test_answer_format_sorted():
    task = GF2MatrixRank()
    for _ in range(20):
        x = task.generate_example()
        pivs = [int(c) for c in x.answer.split(',')]
        assert pivs == sorted(pivs)
        assert all(0 <= c <= min(len(x.metadata['matrix'][0]) - 1, 20) for c in pivs)


def test_difficulty_changes():
    task = GF2MatrixRank()
    task.config.set_level(0)
    l0 = task.config.max_rows
    task.config.set_level(6)
    l6 = task.config.max_rows
    assert l6 > l0


def test_rank_and_pivot_variety_across_levels():
    task = GF2MatrixRank()
    seen_ranks = set()
    for _ in range(200):
        level = random.randint(0, 6)
        task.config.set_level(level)
        x = task.generate_example()
        pivs = [int(c) for c in x.answer.split(',')]
        ncols = len(x.metadata['matrix'][0])
        seen_ranks.add(len(pivs))
        assert len(pivs) == x.metadata['rank']
        assert all(0 <= c < ncols for c in pivs)
    assert len(seen_ranks) >= 4


def test_square_tall_wide_shapes():
    task = GF2MatrixRank()
    tall = wide = square = 0
    for _ in range(300):
        task.config.set_level(random.randint(0, 6))
        x = task.generate_example()
        nr = len(x.metadata['matrix'])
        nc = len(x.metadata['matrix'][0])
        if nr > nc:
            tall += 1
        elif nc > nr:
            wide += 1
        else:
            square += 1
    assert tall > 0 and wide > 0 and square > 0
