import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matroid_two_sum_independence import (  # noqa: E402
    MatroidTwoSumIndependence,
    MatroidTwoSumConfig,
    _independent,
)


def _ex():
    t = MatroidTwoSumIndependence()
    return t, t.generate_example()


def test_generate_and_score():
    t, ex = _ex()
    assert ex.metadata["answer"] in ("yes", "no")
    assert ex.answer == ex.metadata["answer"]
    assert t.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    t, ex = _ex()
    assert t.score_answer("", ex) == 0.0
    assert t.score_answer("maybe", ex) == 0.0
    assert t.score_answer(ex.answer.upper(), ex) == 1.0


def test_wrong_answer_zero():
    t, ex = _ex()
    wrong = "no" if ex.metadata["answer"] == "yes" else "yes"
    assert t.score_answer(wrong, ex) == 0.0


def test_answer_matches_independence():
    t, ex = _ex()
    md = ex.metadata
    assert _independent.__name__  # ensuring importable


def test_config_difficulty_changes_level():
    c = MatroidTwoSumConfig()
    assert c.n_components == 2
    c.set_level(5)
    assert c.n_components == 3
    assert c.nmax > 0


def test_deterministic_seeded():
    import random
    random.seed(7)
    t = MatroidTwoSumIndependence()
    ex1 = t.generate_example()
    random.seed(7)
    t2 = MatroidTwoSumIndependence()
    ex2 = t2.generate_example()
    m1 = {k: v for k, v in ex1.metadata.items() if not k.startswith("_")}
    m2 = {k: v for k, v in ex2.metadata.items() if not k.startswith("_")}
    assert m1 == m2
    assert ex1.answer == ex2.answer
