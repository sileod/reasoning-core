import random
from fractions import Fraction

import pytest

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_counterfactual_r1.adjusted_winner_redivide.adjusted_winner_redivide import (
    AdjustedWinnerRedivide,
    _adjusted_winner,
    _fmt,
)


@pytest.fixture(scope="module")
def task():
    random.seed(12345)
    return AdjustedWinnerRedivide()


def test_generate_and_score(task):
    for _ in range(30):
        ex = task.generate_example()
        assert isinstance(ex, Entry)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_domain_correct(task):
    for _ in range(30):
        ex = task.generate_example()
        meta = ex.metadata
        a = [Fraction(v) for v in meta["valA"]]
        b = [Fraction(v) for v in meta["valB"]]
        frac = [Fraction(v) for v in meta["fracA"]]
        assert sum(a) == 100
        assert sum(b) == 100
        scoreA = sum(a[i] * frac[i] for i in range(len(a)))
        scoreB = sum(b[i] * (1 - frac[i]) for i in range(len(b)))
        assert scoreA == scoreB
        assert scoreA == Fraction(meta["score"])
        assert all(0 <= x <= 1 for x in frac)


def test_adjusted_winner_known_case():
    a = [Fraction(70), Fraction(15)]
    b = [Fraction(30), Fraction(85)]
    f = _adjusted_winner(a, b)
    scoreA = sum(a[i] * f[i] for i in range(2))
    scoreB = sum(b[i] * (1 - f[i]) for i in range(2))
    assert scoreA == scoreB
    assert scoreA == Fraction(289, 4)


def test_junk_rejected(task):
    ex = task.generate_example()
    assert task.score_answer("garbage", ex) == 0
    assert task.score_answer("", ex) == 0
    assert task.score_answer("1/1\n2/2\nscore 3/3", ex) == 0


def test_wrong_fraction_rejected(task):
    ex = task.generate_example()
    meta = ex.metadata
    wrong = "\n".join(_fmt(Fraction(v) + 1) for v in meta["fracA"])
    assert task.score_answer(wrong + "\nscore " + meta["score"], ex) == 0


def test_wrong_score_rejected(task):
    ex = task.generate_example()
    meta = ex.metadata
    assert task.score_answer("\n".join(meta["fracA"]) + "\nscore 1/1", ex) == 0


def test_levels_change_count(task):
    task2 = AdjustedWinnerRedivide()
    task2.config.set_level(0)
    c0 = task2.config.count
    task2.config.set_level(6)
    c6 = task2.config.count
    assert c6 > c0


def test_score_roundtrip_json(task):
    import json
    ex = task.generate_example()
    rt = Entry(metadata=json.loads(json.dumps(dict(ex.metadata))), answer=ex.answer)
    assert task.score_answer(ex.answer, rt) == 1.0
