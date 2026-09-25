"""Tests for the nuisance_contrast_identifiability task."""

from fractions import Fraction

from reasoning_core.tasks.generated.ua_invariants_r4.nuisance_contrast_identifiability.nuisance_contrast_identifiability import (
    _canonical,
    _check_identifiable,
    NuisanceContrastConfig,
    NuisanceContrastIdentifiability,
)


def _approx_equal(a, b):
    return abs(a - b) < 1e-9


def test_check_identifiable_rowspace():
    # x1 - 2 x2 = 3 ;  x2 + x3 = 1
    rows = [([1, -2, 0], Fraction(3)), ([0, 1, 1], Fraction(1))]
    # contrast = 2*(row1) - 1*(row2) = [2,-5,-1]  -> value 2*3 - 1*1 = 5
    contrast = [2, -5, -1]
    ident, val = _check_identifiable(rows, contrast)
    assert ident is True
    assert val == Fraction(5)


def test_check_identifiable_no_rowspace():
    rows = [([1, -1, 0], Fraction(3))]
    # contrast [0,0,1] not in row space of [[1,-1,0]]
    contrast = [0, 0, 1]
    ident, val = _check_identifiable(rows, contrast)
    assert ident is False
    assert val is None


def test_canonical():
    assert _canonical(Fraction(5)) == '5'
    assert _canonical(Fraction(-3, 2)) == '-3/2'


def test_generate_example_roundtrip():
    task = NuisanceContrastIdentifiability()
    task.config = NuisanceContrastConfig()
    ex = task.generate_example()
    md = ex.metadata
    rows = [(list(r), Fraction(rhs)) for r, rhs in md['constraints']]
    ident, val = _check_identifiable(rows, md['contrast'])
    expected = 'identifiable %s' % _canonical(val) if (ident and val is not None) else 'not identifiable'
    assert ex.answer == expected


def test_scoring():
    task = NuisanceContrastIdentifiability()
    task.config = NuisanceContrastConfig()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0
    assert task.score_answer('', ex) == 0.0
    assert task.score_answer('junk', ex) == 0.0
    assert task.score_answer(123, ex) == 0.0


def test_balance_and_difficulty():
    counts = {'ident': 0, 'not': 0}
    task = NuisanceContrastIdentifiability()
    for level in (0, 3, 6):
        cfg = NuisanceContrastConfig()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(40):
            ex = task.generate_example()
            if ex.answer.startswith('identifiable'):
                counts['ident'] += 1
            else:
                counts['not'] += 1
    assert counts['ident'] > 0 and counts['not'] > 0


def test_difficulty_changes_config():
    cfg = NuisanceContrastConfig()
    cfg.set_level(0)
    n0 = cfg.n_params
    cfg.set_level(6)
    n6 = cfg.n_params
    assert n6 > n0
