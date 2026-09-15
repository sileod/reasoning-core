"""Tests for the minimal_unsat_core task."""

import random

from reasoning_core.template import Config

from reasoning_core.tasks.generated.manual_high_value_80_r1.minimal_unsat_core.minimal_unsat_core import (  # noqa: E501
    MinimalUnsatCore,
    MinimalUnsatCoreConfig,
    _check_sat,
    _minimal_unsat_subsets,
)


def test_generate_roundtrip_at_levels():
    task = MinimalUnsatCore()
    for level in (0, 2, 5):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        ws = ex.answer.split()
        assert ws == sorted(ws, key=int)
        assert len(ws) >= 1


def test_config_difficulty_monotonic():
    cfg = MinimalUnsatCoreConfig()
    n0 = cfg.nclauses
    cfg.set_level(5)
    assert cfg.nclauses > n0


def test_wrong_and_junk_scores():
    task = MinimalUnsatCore()
    task.config.set_level(2)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("not a list", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0
    assert task.score_answer("999", ex) == 0.0


def test_full_set_unsat_and_core_unsat():
    random.seed(1234)
    nv, nc, mw = 4, 6, 3
    for _ in range(5):
        clauses = []
        for _ in range(nc):
            width = random.randint(1, mw)
            vars_ = random.sample(range(nv), min(width, nv))
            clauses.append([(v, random.random() < 0.5) for v in vars_])
        if _check_sat(nv, clauses):
            continue
        mus = _minimal_unsat_subsets(nv, clauses)
        for m in mus:
            assert not _check_sat(nv, [clauses[i] for i in m])
            for j in range(len(m)):
                rest = [clauses[i] for i in m if i != m[j]]
                assert _check_sat(nv, rest)
