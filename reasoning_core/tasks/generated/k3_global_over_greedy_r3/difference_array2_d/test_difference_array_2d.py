import random

from reasoning_core.tasks.generated.k3_global_over_greedy_r3.difference_array2_d.difference_array_2d import (
    DifferenceArray2D,
    _apply_rectangles,
    _apply_rectangle_naive,
    _parse_grid,
)


def test_gold_scores_one():
    task = DifferenceArray2D()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = DifferenceArray2D()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0
    assert task.score_answer("1 2; 3 x", ex) == 0.0


def test_wrong_grid_scores_zero():
    task = DifferenceArray2D()
    ex = task.generate_example()
    grid = _parse_grid(ex.answer)
    grid[0][0] += 1
    assert task.score_answer(_format(grid), ex) == 0.0


def _format(grid):
    return "; ".join(" ".join(str(v) for v in row) for row in grid)


def test_answer_matches_metadata_grid():
    task = DifferenceArray2D()
    for _ in range(20):
        ex = task.generate_example()
        assert _parse_grid(ex.answer) == [list(r) for r in ex.metadata["grid"]]


def test_naive_and_difference_array_agree():
    task = DifferenceArray2D()
    for _ in range(30):
        ex = task.generate_example()
        rows, cols = ex.metadata["rows"], ex.metadata["cols"]
        rects = [tuple(r) for r in ex.metadata["rectangles"]]
        assert _apply_rectangles(rows, cols, rects) == ex.metadata["grid"]
        assert _apply_rectangle_naive(rows, cols, rects) == ex.metadata["grid"]


def test_rows_and_cols_match_level():
    task = DifferenceArray2D()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(3):
            ex = task.generate_example()
            md = ex.metadata
            assert md["rows"] == task.config.rows
            assert md["cols"] == task.config.cols
            assert len(md["rectangles"]) == task.config.n_rects
            assert len(md["grid"]) == md["rows"]
            assert all(len(r) == md["cols"] for r in md["grid"])


def test_answer_varies():
    task = DifferenceArray2D()
    answers = {task.generate_example().answer for _ in range(20)}
    assert len(answers) > 12


def test_rectangles_in_bounds():
    task = DifferenceArray2D()
    for _ in range(20):
        ex = task.generate_example()
        rows, cols = ex.metadata["rows"], ex.metadata["cols"]
        for r1, c1, r2, c2, _ in ex.metadata["rectangles"]:
            assert 0 <= r1 < r2 < rows
            assert 0 <= c1 < c2 < cols


def test_reproducible_under_seed():
    random.seed(3536382515)
    a = [DifferenceArray2D().generate_example().answer for _ in range(6)]
    random.seed(3536382515)
    b = [DifferenceArray2D().generate_example().answer for _ in range(6)]
    assert a == b
