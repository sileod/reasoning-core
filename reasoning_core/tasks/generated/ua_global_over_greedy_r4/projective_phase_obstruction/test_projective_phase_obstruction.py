import random

import pytest

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.projective_phase_obstruction.projective_phase_obstruction import (
    ProjectivePhaseObstruction,
    ProjectivePhaseObstructionV2Config,
    _answer,
    _solvable,
    _verify,
)


def test_generate_and_score_roundtrip():
    random.seed(0)
    for level in range(7):
        t = ProjectivePhaseObstruction()
        t.config.set_level(level)
        x = t.generate_example()
        assert t.score_answer(x.answer, x) == 1.0
        if x.answer == "never":
            pass
        else:
            assert int(x.answer) >= 2


def test_scoring_is_exact():
    t = ProjectivePhaseObstruction()
    x = t.generate_example()
    wrong_answers = {"never", "2", "3", "4"}
    assert t.score_answer("  " + x.answer.upper() + " ", x) == 1.0
    assert t.score_answer("", x) == 0.0
    assert t.score_answer("junk", x) == 0.0
    for wrong in wrong_answers - {x.answer}:
        assert t.score_answer(wrong, x) == 0.0


def test_answer_matches_solver():
    random.seed(1)
    t = ProjectivePhaseObstruction()
    t.config.set_level(2)
    for _ in range(30):
        x = t.generate_example()
        rows = x.metadata.payload["rows"]
        defects = x.metadata.payload["defects"]
        if x.answer == "never":
            assert _answer(rows, defects) is None
        else:
            assert _answer(rows, defects) == int(x.answer)
        _verify(rows, defects, _answer(rows, defects))


def test_answer_matches_solver_high_level():
    random.seed(3)
    t = ProjectivePhaseObstruction()
    t.config.set_level(6)
    for _ in range(30):
        x = t.generate_example()
        rows = x.metadata.payload["rows"]
        defects = x.metadata.payload["defects"]
        assert (_answer(rows, defects) is None) == (x.answer == "never")


def test_distribution_has_variety():
    random.seed(2)
    t = ProjectivePhaseObstruction()
    t.config.set_level(5)
    seen = set()
    for _ in range(60):
        seen.add(t.generate_example().answer)
    assert len(seen) >= 3
    assert "never" in seen


def test_difficulty_changes_config():
    c0 = ProjectivePhaseObstructionV2Config()
    c6 = ProjectivePhaseObstructionV2Config()
    c6.set_level(6)
    assert c0 != c6
    assert c6.n_gen > c0.n_gen
    assert c6.coeff_max >= c0.coeff_max
