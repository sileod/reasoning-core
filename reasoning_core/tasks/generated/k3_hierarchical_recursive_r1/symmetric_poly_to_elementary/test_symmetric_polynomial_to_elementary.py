import random

import pytest
from sympy import Rational

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.symmetric_polynomial_to_elementary.symmetric_polynomial_to_elementary import (
    SymmetricPolyToElementary,
    e_monomial,
    parse_answer,
    reconstruct,
    to_elementary,
)


def test_generate_and_score_all_levels():
    task = SymmetricPolyToElementary()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = SymmetricPolyToElementary()
    task.config.set_level(3)
    ex = task.generate_example()
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer("", ex) == 0.0


def test_wrong_answer_scores_zero():
    task = SymmetricPolyToElementary()
    task.config.set_level(2)
    ex = task.generate_example()
    import re
    wrong = re.sub(r":\s*-?\d+(?:/\d+)?", ":0", ex.answer)
    assert task.score_answer(wrong, ex) == 0.0


def test_reconstruct_roundtrip():
    n = 3
    mu = (2, 1, 0)
    emu = e_monomial(mu, n)
    back = reconstruct({mu: 1}, n)
    assert back == emu


def test_to_elementary_identity_simple():
    n = 2
    P = {(2, 0): 1, (1, 1): 1, (0, 2): 1}  # x1^2+x1x2+x2^2 = e1^2 - e2
    exp = to_elementary(P, n)
    assert exp == {(2, 0): 1, (0, 1): -1}


def test_deterministic_under_seed():
    random.seed(12345)
    task = SymmetricPolyToElementary()
    task.config.set_level(3)
    a = task.generate_example()
    random.seed(12345)
    b = task.generate_example()
    assert a.answer == b.answer
    assert a.metadata["polynomial"] == b.metadata["polynomial"]


def test_parse_answer():
    parsed = parse_answer("[(2,0):1/2, (0,1):-3]")
    assert parsed == {(2, 0): Rational(1, 2), (0, 1): -3}