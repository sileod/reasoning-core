# tests/test_complexity.py
import pytest
from reasoning_core.template import Problem
from reasoning_core.tasks.complexity import Complexity, ComplexityConfig


def test_generates_problem():
    task = Complexity()
    ex = task.generate_example()
    assert isinstance(ex, Problem)
    assert ex.prompt
    assert ex.answer in ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)']


def test_score_correct_is_one():
    task = Complexity()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1


def test_score_does_not_use_self():
    """The framework calls score_answer with SelfMock() — must not touch self."""
    from reasoning_core import SelfMock, DATASETS
    task = Complexity()
    ex = task.generate_example()
    # Simulate the framework's invocation pattern
    score = DATASETS['complexity'].score_answer(SelfMock(), ex.answer, ex)
    assert score == 1


def test_score_garbage_does_not_crash():
    task = Complexity()
    ex = task.generate_example()
    # None of these should raise
    for garbage in ['reajrjrje9595!', '', 'import fakemodule', None, 'O(n!)']:
        s = task.score_answer(garbage, ex)
        assert s in (0, 1)


def test_score_wrong_answer_is_zero():
    task = Complexity()
    ex = task.generate_example()
    labels = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)']
    wrong = next(l for l in labels if l != ex.answer)
    assert task.score_answer(wrong, ex) == 0


def test_score_is_normalized():
    """'O(n)', ' O(N) ', 'o(n)' should all score the same."""
    task = Complexity()
    ex = task.generate_example()
    if ex.answer == 'O(n)':
        for variant in ['O(n)', ' O(n) ', 'o(n)', 'O(N)']:
            assert task.score_answer(variant, ex) == 1


def test_set_level_is_invariant_on_c_and_seed():
    task = Complexity()
    task.config.c = 0.5
    task.config.seed = 42
    c_before = task.config.c
    seed_before = task.config.seed
    task.config.set_level(1)
    assert task.config.c == c_before
    assert task.config.seed == seed_before


def test_set_level_roundtrip_restores_config():
    task = Complexity()
    task.config.set_level(2)
    c0 = task.config.to_dict()
    task.config.set_level(0)
    c1 = task.config.to_dict()
    # After roundtrip, 'active_labels_count' should match initial (level 0)
    assert c1['active_labels_count'] == 2


def test_levels_progress_labels():
    """Higher levels should expose more complexity classes."""
    t0 = Complexity()
    t0.config.set_level(0)
    t3 = Complexity()
    t3.config.set_level(3)
    assert t0.config.active_labels_count < t3.config.active_labels_count
    assert t3.config.active_labels_count == 5


def test_balanced_batch():
    """Confirm that generate_balanced_batch works and returns the requested size."""
    task = Complexity()
    batch = task.generate_balanced_batch(batch_size=8, max_tokens=5000)
    assert len(batch) == 8
    for problem in batch:
        assert isinstance(problem, Problem)
        assert problem.prompt
        assert problem.answer in ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)']


def test_framework_validate_hook():
    """The framework's own validate() method must pass."""
    task = Complexity()
    task.validate(n_samples=5)
