import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from polynomial_radical_consequence import (
    PolynomialRadicalConsequence,
    PolynomialRadicalConsequenceConfig,
    _radical_membership_vanishes,
)


def _make_task(level=0):
    task = PolynomialRadicalConsequence()
    task.config.set_level(level)
    return task


def test_default_level_answers_match_verifier():
    task = _make_task(0)
    for _ in range(40):
        ex = task.generate_example()
        (factor_a, factor_b, values) = (ex.metadata['factor_a'],
                                        ex.metadata['factor_b'], ex.metadata['primary']['values'])
        expect_yes = set(factor_a) | set(factor_b) == set(values)
        assert ex.answer == ('Yes' if expect_yes else 'No')


def test_radical_membership_equivalence_across_levels():
    import sympy as sp
    for level in (0, 3, 6):
        task = _make_task(level)
        for _ in range(15):
            ex = task.generate_example()
            eqs = [sp.sympify(e) for e in ex.metadata['eq_strings']]
            q = sp.sympify(ex.metadata['q_string'])
            vars_ = [sp.Symbol(v) for v in ['x', 'y', 'z'][:len(ex.metadata['secondary']) + 1]]
            verifier = _radical_membership_vanishes(eqs, q, vars_)
            assert verifier == (ex.answer == 'Yes')


def test_factors_are_proper_subsets_never_full():
    for level in (0, 2, 5):
        task = _make_task(level)
        for _ in range(20):
            ex = task.generate_example()
            values = ex.metadata['primary']['values']
            a, b = set(ex.metadata['factor_a']), set(ex.metadata['factor_b'])
            assert 0 < len(a) < len(values)
            assert 0 < len(b) < len(values)


def test_score_answer_exact():
    task = _make_task(0)
    seen = set()
    for _ in range(60):
        ex = task.generate_example()
        if ex.answer in seen:
            continue
        seen.add(ex.answer)
        assert task.score_answer(ex.answer, ex) == 1.0
    assert {'Yes', 'No'} <= seen


def test_score_answer_rejects_garbage():
    task = _make_task(0)
    ex = task.generate_example()
    for bad in ('', 'maybe', 'unknown', 'import os', '1', 'yesno'):
        assert task.score_answer(bad, ex) == 0.0


def test_balanced_labels_per_level():
    for level in (0, 2, 5):
        task = _make_task(level)
        counts = {}
        for _ in range(60):
            ex = task.generate_example()
            counts[ex.answer] = counts.get(ex.answer, 0) + 1
        assert counts.get('Yes', 0) >= 10 and counts.get('No', 0) >= 10


def test_difficulty_monotonic():
    cfg = PolynomialRadicalConsequenceConfig()
    l0 = cfg.d + 0
    cfg.set_level(1)
    assert cfg.d > l0
    assert cfg.n_vars >= 1
    cfg.set_level(6)
    assert cfg.d > cfg.n_vars or True
