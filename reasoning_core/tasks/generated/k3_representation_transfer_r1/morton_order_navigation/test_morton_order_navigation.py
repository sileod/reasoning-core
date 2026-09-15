"""Tests for MortonOrderNavigation Z-order navigation."""

import random

from reasoning_core.tasks.generated.k3_representation_transfer_r1.morton_order_navigation.morton_order_navigation import (
    MortonOrderNavigation,
    morton_decode,
    morton_encode,
    _morton_neighbor,
)


def test_roundtrip_consistent():
    for g in range(1, 9):
        for x in range(1 << g):
            for y in range(1 << g):
                z = morton_encode(x, y, g)
                assert morton_decode(z, g) == (x, y)


def test_small_gold():
    g = 3
    assert morton_encode(1, 1, g) == 3
    assert morton_encode(2, 1, g) == 6
    assert morton_decode(5, g) == (3, 0)
    assert morton_encode(0, 0, g) == 0
    assert morton_encode(3, 7, g) == 47
    assert morton_decode(47, g) == (3, 7)


def test_generation_scores_at_levels():
    for level in (0, 2, 5):
        task = MortonOrderNavigation()
        task.config.set_level(level)
        for _ in range(50):
            entry = task.generate_example(level=level)
            assert task.score_answer(entry.answer, entry) == 1


def test_answer_is_computed_index_not_coordinate_echo():
    task = MortonOrderNavigation()
    task.config.set_level(0)
    for _ in range(200):
        entry = task.generate_example(level=0)
        mode = entry.metadata["mode"]
        if mode == "enc":
            x, y = entry.metadata["x"], entry.metadata["y"]
            assert entry.answer == str(morton_encode(x, y, entry.metadata["bits"]))
        elif mode == "dec":
            z = entry.metadata["index"]
            x, y = morton_decode(z, entry.metadata["bits"])
            assert entry.answer == "%d,%d" % (x, y)


def test_neighbor_bounds():
    for g in range(2, 9):
        task = MortonOrderNavigation()
        task.config.bits = g
        for _ in range(200):
            entry = task.generate_entry()
            if entry.metadata["mode"] != "neighbor":
                continue
            x, y, direction = (entry.metadata["x"], entry.metadata["y"],
                               entry.metadata["direction"])
            n = 1 << g
            if direction == "east":
                assert x < n - 1
            elif direction == "west":
                assert x > 0
            elif direction == "north":
                assert y > 0
            else:
                assert y < n - 1


def test_seeded_deterministic():
    def run():
        random.seed(123)
        task = MortonOrderNavigation()
        return [
            (e.prompt, e.answer)
            for _ in range(20)
            for e in [task.generate_example()]
        ]
    assert run() == run()
