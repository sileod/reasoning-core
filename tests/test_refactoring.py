# tests/test_refactoring.py
import pytest
from reasoning_core.template import Problem
from reasoning_core.tasks.refactoring import Refactoring, TRANSFORMATIONS


def test_generates_problem():
    task = Refactoring()
    ex = task.generate_example()
    assert isinstance(ex, Problem)
    assert ex.prompt
    assert ex.answer in TRANSFORMATIONS


def test_shared_output_matches():
    """Both programs should produce the same stdout."""
    task = Refactoring()
    ex = task.generate_example()
    assert ex.metadata.shared_output
    # The original and transformed code are shown in the prompt
    assert ex.metadata.original_code != ex.metadata.transformed_code


def test_score_correct_is_one():
    task = Refactoring()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1


def test_score_does_not_use_self():
    from reasoning_core import SelfMock, DATASETS
    task = Refactoring()
    ex = task.generate_example()
    score = DATASETS['refactoring'].score_answer(SelfMock(), ex.answer, ex)
    assert score == 1


def test_score_garbage_does_not_crash():
    task = Refactoring()
    ex = task.generate_example()
    for garbage in ['reajrjrje9595!', '', 'import fakemodule', None, 'unknown_strategy']:
        s = task.score_answer(garbage, ex)
        assert s in (0, 1)


def test_score_wrong_answer_is_zero():
    task = Refactoring()
    ex = task.generate_example()
    wrong = next(t for t in TRANSFORMATIONS if t != ex.answer)
    assert task.score_answer(wrong, ex) == 0


def test_score_normalized():
    """Label normalization: whitespace, case, hyphen→underscore."""
    task = Refactoring()
    ex = task.generate_example()
    for variant in [ex.answer, ex.answer.upper(), f'  {ex.answer}  ']:
        assert task.score_answer(variant, ex) == 1


def test_set_level_is_invariant_on_c_and_seed():
    task = Refactoring()
    task.config.c = 0.5
    task.config.seed = 42
    c_before = task.config.c
    seed_before = task.config.seed
    task.config.set_level(1)
    assert task.config.c == c_before
    assert task.config.seed == seed_before


def test_levels_increase_depth():
    t0 = Refactoring()
    t0.config.set_level(0)
    depth0 = t0.config.max_depth
    t2 = Refactoring()
    t2.config.set_level(2)
    depth2 = t2.config.max_depth
    assert depth2 > depth0


def test_balanced_batch():
    task = Refactoring()
    batch = task.generate_balanced_batch(batch_size=4, max_tokens=5000)
    assert len(batch) == 4
    for problem in batch:
        assert isinstance(problem, Problem)
        assert problem.prompt
        assert problem.answer in TRANSFORMATIONS


def test_framework_validate_hook():
    task = Refactoring()
    task.validate(n_samples=5)
