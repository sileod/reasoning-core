import pytest

from reasoning_core.tasks.generated.k3_non_local_structured_r4.heap_splitting_nimber_recursion.heap_split_nimber import (
    HeapSplitNimber,
    _NimberSolver,
    _xor,
)


def test_nimber_low_heaps():
    solver = _NimberSolver([[] for _ in range(8)])
    assert solver.nimber(0) == 0


def test_xor_combines_subheaps():
    assert _xor([1, 2, 3]) == 0
    assert _xor([5, 6]) == 3


def test_generate_and_score_gold():
    task = HeapSplitNimber()
    task.config.set_level(3)
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1.0


def test_score_garbage():
    task = HeapSplitNimber()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("abc", entry) == 0.0


@pytest.mark.parametrize("level", [0, 3, 6])
def test_all_levels_generate(level):
    task = HeapSplitNimber()
    task.config.set_level(level)
    task.generate_example()
