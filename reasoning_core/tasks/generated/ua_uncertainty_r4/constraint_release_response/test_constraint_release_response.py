import random

import pytest
import sympy as sp

from reasoning_core.tasks.generated.ua_uncertainty_r4.constraint_release_response.constraint_release_response import (
    ConstraintReleaseResponse,
    _fmt,
    _parse_fraction,
)


def test_gold_scores_one_at_all_levels():
    task = ConstraintReleaseResponse()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(12):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0, (level, ex.answer)


def test_junk_does_not_score():
    task = ConstraintReleaseResponse()
    ex = task.generate_example()
    for junk in ("", "abc", "import os", "None", "3.14", "1/0", "-", "+", "//"):
        assert task.score_answer(junk, ex) != 1.0, junk


def test_answer_format_and_domain():
    task = ConstraintReleaseResponse()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(12):
            ex = task.generate_example()
            meta = ex.metadata
            delta = sp.Rational(meta["change_num"], meta["change_den"])
            assert meta["change_den"] > 0
            assert delta != 0
            assert _fmt(delta) == ex.answer


def test_parse_fraction_edges():
    assert _parse_fraction("3/4") == sp.Rational(3, 4)
    assert _parse_fraction("-1/2") == sp.Rational(-1, 2)
    assert _parse_fraction("0") == sp.Rational(0)
    assert _parse_fraction("2") == sp.Rational(2)
    assert _parse_fraction("-7/3") == sp.Rational(-7, 3)
    assert _parse_fraction("") is None
    assert _parse_fraction("1/0") is None
    assert _parse_fraction("abc") is None


def test_difficulty_changes_config():
    task = ConstraintReleaseResponse()
    task.config.set_level(1)
    assert task.config != ConstraintReleaseResponse().config


def test_negative_and_positive_answers_occur():
    task = ConstraintReleaseResponse()
    task.config.set_level(5)
    neg = pos = 0
    for _ in range(60):
        ex = task.generate_example()
        if ex.answer.startswith("-"):
            neg += 1
        else:
            pos += 1
    assert neg > 0 and pos > 0
