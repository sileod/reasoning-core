import random

import pytest

from reasoning_core.tasks.generated.ua_formal_semantics_r4.negative_concord_interpretation.negative_concord_interpretation import (
    NegativeConcordInterpretation,
    _overall,
    _licensed,
    _clause_pol,
)


def test_generate_returns_valid_answer():
    t = NegativeConcordInterpretation()
    random.seed(1)
    for _ in range(50):
        e = t.generate_example()
        assert e.answer in ('negated', 'asserted', 'unlicensed')
        assert isinstance(e.metadata['sentence'], str)


def test_overall_matches_computed_answer():
    for within in ('concord', 'double_neg'):
        for barrier in ('barrier_on', 'barrier_off'):
            # single clause, no negatives -> asserted
            assert _overall([0], [False], [False], within, barrier) == 'asserted'
            # single clause, one negative -> negated
            assert _overall([1], [True], [False], within, barrier) == 'negated'
            # concord: two negatives in one clause -> one negation (negated)
            assert _overall([2], [True], [False], 'concord', 'barrier_on') == 'negated'
            # double_neg: two negatives -> parity 0 -> asserted
            assert _overall([2], [True], [False], 'double_neg', 'barrier_on') == 'asserted'


def test_unlicensed_detection():
    # embedded NI with no overt negator and matrix not negated -> unlicensed
    assert _overall([0, 1], [True, False], [False, True], 'concord', 'barrier_on') == 'unlicensed'
    # matrix negated licenses embedded NI
    assert _overall([1, 1], [True, False], [False, True], 'concord', 'barrier_on') != 'unlicensed'
    # embedded overt negator licenses
    assert _overall([0, 1], [True, True], [False, True], 'concord', 'barrier_on') != 'unlicensed'


def test_score_answer():
    t = NegativeConcordInterpretation()
    random.seed(7)
    e = t.generate_example()
    assert t.score_answer(e.answer, e) == 1.0
    assert t.score_answer('negated', e) in (0.0, 1.0)
    assert t.score_answer('', e) == 0.0
    assert t.score_answer('foo', e) == 0.0
    assert t.score_answer(None, e) == 0.0


def test_levels_generate():
    for level in (0, 1, 2, 3, 4, 5, 6):
        t = NegativeConcordInterpretation()
        t.config.set_level(level)
        random.seed(level)
        e = t.generate_example()
        assert isinstance(e.answer, str)
