import pytest

from reasoning_core.tasks.generated.ua_formal_logic_r4.resolution_interpolant_extraction.resolution_interpolant_extraction import (
    ResolutionInterpolantExtraction,
)


def _task(level=2):
    t = ResolutionInterpolantExtraction()
    t.config.set_level(level)
    return t


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_generate_and_score_all_levels(level):
    task = _task(level)
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_answer_is_binary_truth_string():
    task = _task(2)
    e = task.generate_example()
    w = len(e.metadata["shared_atoms"])
    assert len(e.answer) == 2 ** w
    assert set(e.answer) <= {"0", "1"}


def test_shared_atoms_positive():
    task = _task(2)
    for _ in range(30):
        e = task.generate_example()
        n = len(e.metadata["shared_atoms"])
        assert n >= 1


def test_changes_with_level_and_no_reseed(capsys):
    t0 = _task(0)
    t6 = _task(6)
    assert t6.config.num_roots > t0.config.num_roots


def test_junk_scores_zero():
    task = _task(2)
    e = task.generate_example()
    assert round(task.score_answer("111", e), 1) == 0.0
    assert round(task.score_answer("", e), 1) == 0.0
