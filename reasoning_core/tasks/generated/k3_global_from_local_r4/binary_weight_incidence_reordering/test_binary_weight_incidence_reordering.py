import os
import random
import sys

from reasoning_core.template import Config, Entry, Task

sys.path.insert(0, os.path.dirname(__file__))
import binary_weight_incidence_reordering as mod
from binary_weight_incidence_reordering import BinaryWeightIncidenceReordering


def _row_key(row):
    return (-sum(row), tuple(-b for b in row))


def test_generation_and_score():
    task = BinaryWeightIncidenceReordering()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            x = task.generate_entry()
            assert task.score_answer(x.answer, x) == 1.0


def test_wrong_answers_zero():
    task = BinaryWeightIncidenceReordering()
    task.config.set_level(2)
    x = task.generate_entry()
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer("", x) == 0.0
    nrow = x.metadata["nrow"]
    bad = list(range(nrow - 1, -1, -1))
    assert task.score_answer(str(bad), x) == 0.0


def test_difficulty_changes_config():
    task = BinaryWeightIncidenceReordering()
    task.config.set_level(0)
    n0 = task.config.nrow
    task.config.set_level(6)
    n6 = task.config.nrow
    assert n6 > n0


def test_score_is_consistent_with_perm():
    task = BinaryWeightIncidenceReordering()
    task.config.set_level(3)
    x = task.generate_entry()
    matrix = [tuple(r) for r in x.metadata["matrix"]]
    order = list(range(x.metadata["nrow"]))
    order.sort(key=lambda i: _row_key(matrix[i]))
    assert x.metadata["perm"] == order
    assert x.answer == str(order)
