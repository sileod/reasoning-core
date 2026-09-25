import random

import pytest

from reasoning_core.template import Entry

from .renormalization_forest_subtraction import (
    RenormalizationForestSubtraction, renorm_forest,
)


@pytest.fixture()
def task():
    return RenormalizationForestSubtraction()


def _valid(node):
    weight, mod, div, kids = node
    assert isinstance(weight, int) and weight >= 1
    if div:
        assert isinstance(mod, int) and mod >= 2
    for k in kids:
        _valid(k)


def test_gold_scores(task):
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
            for root in x.metadata["forest"]:
                _valid(root)
            assert isinstance(x.metadata["forest"], list)


def test_bad_answers(task):
    task.config.set_level(1)
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer(None, x) < 1.0
    assert task.score_answer("abc", x) < 1.0
    assert task.score_answer(str(int(x.answer) + 1), x) < 1.0


def test_domains(task):
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            x = task.generate_example()
            assert int(x.answer) >= 0


def test_level_scales(task):
    base = task.config.__class__()
    lo = task.config.__class__()
    lo.set_level(0)
    hi = task.config.__class__()
    hi.set_level(6)
    assert hi.max_depth >= lo.max_depth
    assert hi.modulus_hi >= lo.modulus_hi


def test_deterministic(task):
    random.seed(123)
    a = task.generate_example().answer
    random.seed(123)
    b = task.generate_example().answer
    assert a == b
