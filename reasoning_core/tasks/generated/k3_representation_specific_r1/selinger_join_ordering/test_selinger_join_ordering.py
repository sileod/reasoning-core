import pytest

from reasoning_core.tasks.generated.k3_representation_specific_r1.selinger_join_ordering.selinger_join_ordering import (
    SelingerJoinOrdering,
    _optimal_join_cost,
)


@pytest.mark.parametrize("level", [0, 3, 6])
def test_generate_and_score(level):
    task = SelingerJoinOrdering()
    task.config.set_level(level)
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0
        assert task.score_answer("", e) < 1.0
        assert task.score_answer("junk", e) < 1.0
        assert int(e.answer) >= 0


def test_deterministic_cost():
    adjacency = [[[1, 5]], [[0, 5], [2, 3]], [[1, 3]]]
    c = _optimal_join_cost(adjacency, [2, 3, 4])
    assert isinstance(c, int)
    assert c >= 0


def test_score_formats():
    task = SelingerJoinOrdering()
    task.config.set_level(1)
    e = task.generate_example()
    assert task.score_answer(e.answer, e) == 1.0
    assert task.score_answer(f"{int(e.answer)}.0", e) == 1.0
    assert task.score_answer(str(int(e.answer) + 1), e) < 1.0
