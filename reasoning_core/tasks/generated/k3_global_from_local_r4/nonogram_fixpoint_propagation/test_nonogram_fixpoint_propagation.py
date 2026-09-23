import random

from reasoning_core.tasks.generated.k3_global_from_local_r4.nonogram_fixpoint_propagation.nonogram_fixpoint_propagation import (
    NonogramFixpointPropagation,
    _fixpoint,
    _possible_fills,
    _line_clues,
)


def test_round_trip_scores_1():
    random.seed(1234)
    task = NonogramFixpointPropagation()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_answers_are_canonical():
    random.seed(1)
    task = NonogramFixpointPropagation()
    for _ in range(30):
        ex = task.generate_example()
        assert ex.answer in ('B', 'W', '?')


def test_junk_and_empty_not_full():
    random.seed(2)
    task = NonogramFixpointPropagation()
    for _ in range(10):
        ex = task.generate_example()
        assert task.score_answer('', ex) < 1.0
        assert task.score_answer('xyz', ex) < 1.0


def test_generated_grid_is_consistent_with_clues():
    random.seed(3)
    task = NonogramFixpointPropagation()
    for _ in range(20):
        ex = task.generate_example()
        md = ex.metadata
        size = md['size']
        grid = md['grid']
        row_clues = [tuple(x) for x in md['row_clues']]
        col_clues = [tuple(x) for x in md['col_clues']]
        for r in range(size):
            assert _line_clues(grid[r]) == row_clues[r]
        for c in range(size):
            assert _line_clues([grid[r][c] for r in range(size)]) == col_clues[c]


def test_force_is_stable():
    random.seed(4)
    task = NonogramFixpointPropagation()
    for _ in range(15):
        ex = task.generate_example()
        md = ex.metadata
        size = md['size']
        row_clues = [tuple(x) for x in md['row_clues']]
        col_clues = [tuple(x) for x in md['col_clues']]
        c1 = _fixpoint(size, row_clues, col_clues)
        c2 = _fixpoint(size, row_clues, col_clues)
        assert c1 == c2


def test_levels_generate():
    task = NonogramFixpointPropagation()
    for level in range(7):
        task.config.set_level(level)
        assert task.generate_example().answer in ('B', 'W', '?')
