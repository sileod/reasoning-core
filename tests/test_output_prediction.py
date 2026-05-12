# tests/test_output_prediction.py
import pytest
from reasoning_core.template import Problem
from reasoning_core.tasks.output_prediction import OutputPrediction


def test_generates_problem():
    task = OutputPrediction()
    ex = task.generate_example()
    assert isinstance(ex, Problem)
    assert ex.prompt
    assert ex.answer
    assert len(ex.answer.strip()) > 0


def test_score_correct_is_one():
    """Exact match of the reference answer should score 1.0."""
    task = OutputPrediction()
    ex = task.generate_example()
    # Scoring is fuzzy, but the reference itself should score 1.0
    score = task.score_answer(ex.answer, ex)
    assert score == 1.0


def test_score_does_not_use_self():
    from reasoning_core import SelfMock, DATASETS
    task = OutputPrediction()
    ex = task.generate_example()
    score = DATASETS['output_prediction'].score_answer(SelfMock(), ex.answer, ex)
    assert score == 1.0


def test_score_garbage_does_not_crash():
    task = OutputPrediction()
    ex = task.generate_example()
    for garbage in ['reajrjrje9595!', '', 'import fakemodule', None, '   ']:
        s = task.score_answer(garbage, ex)
        assert 0 <= s <= 1


def test_score_wrong_answer_is_less_than_one():
    """A very different answer should score well below 1."""
    task = OutputPrediction()
    ex = task.generate_example()
    wrong = "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
    s = task.score_answer(wrong, ex)
    assert s < 0.9


def test_score_is_symmetric_on_whitespace():
    """Leading/trailing whitespace shouldn't affect the score."""
    task = OutputPrediction()
    ex = task.generate_example()
    padded = f"   {ex.answer}   "
    s = task.score_answer(padded, ex)
    assert s == 1.0


def test_set_level_is_invariant_on_c_and_seed():
    task = OutputPrediction()
    task.config.c = 0.5
    task.config.seed = 42
    c_before = task.config.c
    seed_before = task.config.seed
    task.config.set_level(1)
    assert task.config.c == c_before
    assert task.config.seed == seed_before


def test_levels_increase_depth():
    t0 = OutputPrediction()
    t0.config.set_level(0)
    depth0 = t0.config.max_depth
    t2 = OutputPrediction()
    t2.config.set_level(2)
    depth2 = t2.config.max_depth
    assert depth2 > depth0


def test_balanced_batch():
    task = OutputPrediction()
    batch = task.generate_balanced_batch(batch_size=4, max_tokens=5000)
    assert len(batch) == 4
    for problem in batch:
        assert isinstance(problem, Problem)
        assert problem.prompt
        assert len(problem.answer.strip()) > 0


def test_framework_validate_hook():
    task = OutputPrediction()
    task.validate(n_samples=5)
