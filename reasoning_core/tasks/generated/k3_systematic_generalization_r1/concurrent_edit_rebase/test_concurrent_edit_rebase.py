"""Tests for the ConcurrentEditRebase task."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))

from concurrent_edit_rebase import (
    ConcurrentEditRebase,
    _noop_valid,
    _rebase,
)


def _check(entry, task):
    assert task.score_answer(entry.answer, entry) == 1.0


def test_gold_scores_one_at_each_level():
    task = ConcurrentEditRebase()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_example()
            _check(e, task)


def test_answers_vary():
    task = ConcurrentEditRebase()
    answers = set()
    for _ in range(200):
        answers.add(task.generate_example().answer)
    assert len(answers) > 3


def test_all_answer_regimes_occur():
    task = ConcurrentEditRebase()
    answers = [task.generate_example().answer for _ in range(400)]
    assert any(a == "no-op" for a in answers)
    assert any(a.startswith("insert") for a in answers)
    assert any(a.startswith("delete") for a in answers)


def test_noop_only_when_valid():
    random.seed(7)
    task = ConcurrentEditRebase()
    task.config.set_level(3)
    for _ in range(300):
        e = task.generate_example()
        A = tuple(e.metadata["A"])
        B = tuple(e.metadata["B"])
        bp = _rebase(A, B)
        if bp is None:
            assert _noop_valid(A, B)
            assert e.answer == "no-op"


def test_rebase_matches_generated_answer():
    random.seed(11)
    task = ConcurrentEditRebase()
    task.config.set_level(4)
    for _ in range(500):
        e = task.generate_example()
        A = tuple(e.metadata["A"])
        B = tuple(e.metadata["B"])
        bp = _rebase(A, B)
        if bp is None:
            assert e.answer == "no-op"
        elif bp[0] == "ins":
            assert e.answer == "insert %d" % bp[1]
        else:
            assert e.answer == "delete %d %d" % (bp[1], bp[2])
