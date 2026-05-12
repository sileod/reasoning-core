# tests/test_runnability.py
import pytest
from reasoning_core.template import Problem
from reasoning_core.tasks.runnability import Runnability


def test_generates_problem():
    task = Runnability()
    ex = task.generate_example()
    assert isinstance(ex, Problem)
    assert ex.prompt
    assert ex.answer in ('runnable', 'error')


def test_score_correct_is_one():
    task = Runnability()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1


def test_score_does_not_use_self():
    from reasoning_core import SelfMock, DATASETS
    task = Runnability()
    ex = task.generate_example()
    score = DATASETS['runnability'].score_answer(SelfMock(), ex.answer, ex)
    assert score == 1


def test_score_garbage_does_not_crash():
    task = Runnability()
    ex = task.generate_example()
    for garbage in ['reajrjrje9595!', '', 'import fakemodule', None, 'maybe']:
        s = task.score_answer(garbage, ex)
        assert s in (0, 1)


def test_score_wrong_answer_is_zero():
    task = Runnability()
    ex = task.generate_example()
    wrong = 'error' if ex.answer == 'runnable' else 'runnable'
    assert task.score_answer(wrong, ex) == 0


def test_score_normalized():
    task = Runnability()
    ex = task.generate_example()
    for variant in [ex.answer, ex.answer.upper(), f' {ex.answer} ', ex.answer.capitalize()]:
        assert task.score_answer(variant, ex) == 1


def test_set_level_is_invariant_on_c_and_seed():
    task = Runnability()
    task.config.c = 0.5
    task.config.seed = 42
    c_before = task.config.c
    seed_before = task.config.seed
    task.config.set_level(1)
    assert task.config.c == c_before
    assert task.config.seed == seed_before


def test_levels_increase_depth():
    t0 = Runnability()
    t0.config.set_level(0)
    depth0 = t0.config.max_depth
    t2 = Runnability()
    t2.config.set_level(2)
    depth2 = t2.config.max_depth
    assert depth2 > depth0


def test_balanced_batch():
    task = Runnability()
    batch = task.generate_balanced_batch(batch_size=6, max_tokens=5000)
    assert len(batch) == 6
    labels = {p.answer for p in batch}
    # Expect both labels in a batch of 6 (balancing_key_ratio=0.5 → max 3 per label)
    assert labels == {'runnable', 'error'}


def test_framework_validate_hook():
    task = Runnability()
    task.validate(n_samples=5)
