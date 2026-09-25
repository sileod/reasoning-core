import random

import pytest

from reasoning_core.tasks.generated.ua_invariants_r4.effective_boundary_response.effective_boundary_response import (
    EffectiveBoundaryResponse,
    parse_ratio,
    rat_str,
)


def test_examples_score_one():
    random.seed(7)
    task = EffectiveBoundaryResponse()
    for _ in range(60):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


@pytest.mark.parametrize("mode", ["A", "B", "C"])
def test_all_modes_occur(mode):
    random.seed(11)
    task = EffectiveBoundaryResponse()
    seen = set()
    for _ in range(200):
        x = task.generate_example()
        seen.add(x.metadata["mode"])
        assert task.score_answer(x.answer, x) == 1.0
    assert mode in seen


def test_junk_scores_zero():
    random.seed(3)
    task = EffectiveBoundaryResponse()
    for _ in range(40):
        x = task.generate_example()
        assert task.score_answer("", x) < 1.0
        assert task.score_answer("garbage", x) < 1.0


def test_mode_b_balanced():
    random.seed(5)
    task = EffectiveBoundaryResponse()
    yes = no = 0
    for _ in range(240):
        x = task.generate_example()
        if x.metadata["mode"] == "B":
            if x.answer == "yes":
                yes += 1
            else:
                no += 1
    total = yes + no
    assert total > 0
    assert 0.2 < yes / total < 0.8


def test_difficulty_levels():
    task = EffectiveBoundaryResponse()
    for level in (0, 1, 3, 6):
        cfg = task.config_cls()
        cfg.set_level(level)
        assert cfg.hidden == 2 + 2 * level


def test_rat_helpers():
    assert rat_str(6) == "6"
    assert rat_str(__import__("sympy").Rational(3, 7)) == "3/7"
    assert parse_ratio("3/7") == __import__("sympy").Rational(3, 7)
    assert parse_ratio("nope") is None


def test_validate():
    task = EffectiveBoundaryResponse()
    task.validate()
