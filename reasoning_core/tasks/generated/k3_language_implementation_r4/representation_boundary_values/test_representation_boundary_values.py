import random

import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_language_implementation_r4.representation_boundary_values.representation_boundary_values import (
    RepresentationBoundaryValues,
    _signed8,
    _simulate,
)


@pytest.fixture
def task():
    return RepresentationBoundaryValues()


def test_example_scores_one(task):
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_tokens_vs_answer(task):
    for _ in range(300):
        ex = task.generate_example()
        assert ex.answer == ", ".join(ex.metadata["tokens"])


def test_no_trap_after_token(task):
    for _ in range(300):
        ex = task.generate_example()
        tokens = ex.metadata["tokens"]
        if "trap" in tokens:
            assert tokens[-1] == "trap"


def test_wrong_answer_not_one(task):
    ex = task.generate_example()
    assert task.score_answer(ex.answer + "x", ex) == 0.0
    assert task.score_answer("trap", ex) == 0.0


def test_checkpoints_grow_by_level():
    t0 = RepresentationBoundaryValues()
    t0.config.set_level(0)
    c0 = t0.config.checkpoints
    t6 = RepresentationBoundaryValues()
    t6.config.set_level(6)
    assert t6.config.checkpoints > c0


def test_score_empty_junk(task):
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0


def test_signed8_roundtrip():
    for b in range(256):
        s = _signed8(b)
        expected = b - 256 if b >= 128 else b
        assert s == expected
        assert (s & 0xFF) == b


def test_levels_all_generate():
    for level in range(7):
        t = RepresentationBoundaryValues()
        t.config.set_level(level)
        for _ in range(20):
            ex = t.generate_entry()
            assert len(ex.metadata["tokens"]) >= 1


def test_reference_selfcheck(task):
    for _ in range(200):
        t = RepresentationBoundaryValues()
        t.config.set_level(random.randrange(7))
        ex = t.generate_entry()
        ops = ex.metadata["checkpoints"]
        v0 = ex.metadata["initial_byte"]
        assert _simulate(ops, v0) == ex.metadata["tokens"]
