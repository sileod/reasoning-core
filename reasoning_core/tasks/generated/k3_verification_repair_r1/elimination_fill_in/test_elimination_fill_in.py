import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import random

from elimination_fill_in import EliminationFillIn


def test_modes_present():
    random.seed(798610012)
    task = EliminationFillIn()
    task.config.set_level(2)
    modes = set()
    for _ in range(40):
        x = task.generate_entry()
        modes.add(x.metadata["mode"])
    assert modes == {"list", "size", "largest"}


def test_scores():
    random.seed(1)
    task = EliminationFillIn()
    task.config.set_level(0)
    for _ in range(30):
        x = task.generate_entry()
        assert task.score_answer(x.answer, x) == 1.0
        if x.metadata["mode"] == "list":
            assert task.score_answer("", x) == 0.0
        else:
            assert task.score_answer(f"{int(x.answer) + 1}", x) == 0.0


def test_all_levels():
    random.seed(2)
    task = EliminationFillIn()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            x = task.generate_entry()
            assert task.score_answer(x.answer, x) == 1.0
            assert task.render_prompt(x.metadata)


def test_fill_edges_reproducible_constructor():
    n = 6
    order = [3, 0, 5, 1, 4, 2]
    adj = [set(a) for a in [[1, 2], [0, 5], [0, 3], [2, 4], [3, 5], [1, 4]]]
    edges = _test_fill(n, order, adj)
    assert isinstance(edges, list)


def _test_fill(n, order, adjacency):
    from elimination_fill_in import _fill_edges
    return _fill_edges(n, order, adjacency)
