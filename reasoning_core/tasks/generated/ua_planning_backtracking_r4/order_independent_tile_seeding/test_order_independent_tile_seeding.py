import random

import pytest

from reasoning_core.tasks.generated.ua_planning_backtracking_r4.order_independent_tile_seeding.order_independent_tile_seeding import (
    OrderIndependentTileSeeding,
    _closure,
)


def test_entry_and_score():
    random.seed(0)
    task = OrderIndependentTileSeeding()
    task.config.set_level(2)
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1
    assert task.score_answer("IMPOSSIBLE", entry) < 1
    assert task.score_answer("", entry) < 1


def test_levels_generate_and_score():
    random.seed(1)
    task = OrderIndependentTileSeeding()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(5):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1


def test_gold_is_forcing():
    random.seed(2)
    task = OrderIndependentTileSeeding()
    task.config.set_level(4)
    e = task.generate_example()
    rows, cols, tau, faces = (
        e.metadata["rows"],
        e.metadata["cols"],
        e.metadata["tau"],
        e.metadata["faces"],
    )
    seed = [int(c) for c in e.answer.split(",")]
    assert _closure(rows * cols, cols, faces, tau, seed) == set(
        range(rows * cols)
    )


def test_gold_is_minimal_forcing():
    random.seed(3)
    task = OrderIndependentTileSeeding()
    task.config.set_level(3)
    e = task.generate_example()
    rows, cols, tau, faces = (
        e.metadata["rows"],
        e.metadata["cols"],
        e.metadata["tau"],
        e.metadata["faces"],
    )
    ans = [int(c) for c in e.answer.split(",")]
    from reasoning_core.tasks.generated.ua_planning_backtracking_r4.order_independent_tile_seeding.order_independent_tile_seeding import (
        _min_forcing_seed,
    )

    assert _min_forcing_seed(rows, cols, faces, tau) == ans
