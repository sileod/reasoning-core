"""Tests for conserved_resource_bound task."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from conserved_resource_bound_model import (  # noqa: E402
    ConservedResourceBound,
    _min_stock,
)


@pytest.fixture(scope="module")
def task():
    return ConservedResourceBound()


def test_summary_and_design_choice_present():
    assert "conserved" in ConservedResourceBound.summary.lower()
    assert ConservedResourceBound.design_choice.startswith(
        "Instances provide a set of alternative recipes sharing coproducts"
    )


def test_generate_entry_and_score(task):
    x = task.generate_example()
    assert x.answer is not None
    assert task.score_answer(x.answer, x) == 1.0


def test_wrong_and_junk_score_zero(task):
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("abc", x) == 0.0
    gold = int(x.answer)
    assert task.score_answer(str(gold + 1), x) == 0.0


def test_answer_is_integer(task):
    for _ in range(10):
        x = task.generate_example()
        assert int(x.answer) >= 0


def test_min_stock_matches_gold(task):
    for _ in range(10):
        x = task.generate_example()
        m = x.metadata
        ms = _min_stock(m["recipes"], m["seed_resource"], m["target_resource"],
                        m["required"])
        assert ms == int(x.answer)


def test_metadata_json_serializable(task):
    import json

    for _ in range(5):
        x = task.generate_example()
        json.dumps(dict(x.metadata))


def test_difficulty_applies():
    t = ConservedResourceBound()
    t.config.set_level(6)
    assert t.config.max_recipe_count >= 2


def test_levels_generate(task):
    t = ConservedResourceBound()
    for level in (0, 2, 5, 6):
        t.config.set_level(level)
        x = t.generate_example()
        assert t.score_answer(x.answer, x) == 1.0
