import itertools
import random

import pytest

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.plural_predication_readings.plural_predication_readings import (
    PluralConfig,
    PluralPredicationReadings,
    _verdicts,
    exact_score,
)


@pytest.fixture
def task():
    return PluralPredicationReadings()


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_all_levels_generate(level):
    t = PluralPredicationReadings()
    cfg = PluralConfig()
    cfg.set_level(level)
    t.config = cfg
    for _ in range(10):
        entry = t.generate_entry()
        assert int(entry.metadata["atoms"]) in (3, 4)
        assert int(entry.metadata["arity"]) in (1, 2)
        assert exact_score(entry.answer, entry) == 1.0


@pytest.mark.parametrize("level", [0, 2, 5])
def test_gold_scores_one(level):
    t = PluralPredicationReadings()
    cfg = PluralConfig()
    cfg.set_level(level)
    t.config = cfg
    entry = t.generate_entry()
    assert exact_score(entry.answer, entry) == 1.0


def test_junk_scores_below_one(task):
    entry = task.generate_entry()
    assert exact_score("", entry) == 0.0
    assert exact_score("x", entry) == 0.0
    assert exact_score(None, entry) == 0.0


def test_verdicts_accumulate():
    unary = [1, 0, 1]
    binary = [[0, 0, 1], [0, 1, 1], [1, 0, 0]]
    masks = [m for m in itertools.product([0, 1], repeat=3) if sum(m) >= 2]
    for arity in (1, 2):
        for m in masks:
            subset = [i for i, b in enumerate(m) if b]
            if arity == 1:
                exp_dist = all(unary[i] for i in subset)
                exp_coll = any(unary[i] for i in subset)
            else:
                exp_dist = all(any(binary[a][b] for b in subset) for a in subset)
                exp_coll = any(binary[a][b] for a in subset for b in subset)
            (d, c, u) = _verdicts([m], arity, unary, binary)[0]
            assert d == int(exp_dist)
            assert c == int(exp_coll)
            assert u == int(exp_dist or exp_coll)


def test_difficulty_changes():
    cfg = PluralConfig()
    before_atoms = cfg.atoms
    cfg.set_level(6)
    assert cfg.atoms >= before_atoms
