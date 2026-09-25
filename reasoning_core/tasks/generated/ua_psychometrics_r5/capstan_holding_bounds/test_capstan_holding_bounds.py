import pytest
from fractions import Fraction

from reasoning_core.tasks.generated.ua_psychometrics_r5.capstan_holding_bounds.capstan_holding_bounds import (
    CapstanHoldingBounds,
    _parse_answer,
)

TASK = CapstanHoldingBounds()


def _expected(entry):
    total = Fraction(entry.metadata["total_tension"])
    product = Fraction(entry.metadata["wrap_product"])
    return total / product, total * product


def test_generate_and_score():
    entry = TASK.generate_entry()
    assert TASK.score_answer(entry.answer, entry) == 1.0


def test_answer_matches_computed_interval():
    for _ in range(200):
        entry = TASK.generate_entry()
        lo, hi = _parse_answer(entry.answer)
        elo, ehi = _expected(entry)
        assert lo == elo
        assert hi == ehi
        assert 0 < lo <= hi


def test_wrong_answer_scores_zero():
    entry = TASK.generate_entry()
    assert TASK.score_answer("", entry) == 0.0
    assert TASK.score_answer("not an answer", entry) == 0.0
    assert TASK.score_answer("[1, 2]", entry) == 0.0
    assert TASK.score_answer("5", entry) == 0.0
    assert TASK.score_answer(None, entry) == 0.0


def test_answer_is_fraction_pair():
    entry = TASK.generate_entry()
    lo, hi = _parse_answer(entry.answer)
    assert lo > 0
    assert hi >= lo


def test_levels_generate():
    for level in range(7):
        cfg = CapstanHoldingBounds().config_cls()
        cfg.set_level(level)
        TASK.config = cfg
        for _ in range(20):
            entry = TASK.generate_entry()
            assert TASK.score_answer(entry.answer, entry) == 1.0


def test_no_degenerate_single_point():
    for _ in range(200):
        entry = TASK.generate_entry()
        lo, hi = _parse_answer(entry.answer)
        assert hi > lo


def test_validate():
    TASK.validate()
