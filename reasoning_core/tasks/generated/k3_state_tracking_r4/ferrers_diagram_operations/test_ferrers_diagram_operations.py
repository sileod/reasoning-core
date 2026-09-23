import pytest

from reasoning_core.tasks.generated.k3_state_tracking_r4.ferrers_diagram_operations.ferrers_diagram_operations import (
    FerrersDiagramOperations,
    _conjugate,
    _hook_length,
    _count_syt_fact,
)


def test_known_conjugate():
    assert _conjugate([4, 2, 1]) == [3, 2, 1, 1]
    assert _conjugate([3, 2]) == [2, 2, 1]


def test_known_hook():
    # partition [4,2,1], cell (0,0) hook = 4-0-1 + (#below>0) + 1 = 3 + 2 + 1 = 6
    assert _hook_length(0, 0, [4, 2, 1]) == 6
    assert _hook_length(1, 0, [4, 2, 1]) == 3


def test_known_syt_count():
    assert _count_syt_fact([4, 2, 1]) == 35
    assert _count_syt_fact([3, 2]) == 5
    assert _count_syt_fact([1, 1]) == 1


def test_roundtrip_all_levels():
    task = FerrersDiagramOperations()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(30):
            e = task.generate_entry()
            assert task.score_answer(e.answer, e) == 1.0


def test_scorer_rejects_junk():
    task = FerrersDiagramOperations()
    e = task.generate_entry()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("banana", e) < 1.0
