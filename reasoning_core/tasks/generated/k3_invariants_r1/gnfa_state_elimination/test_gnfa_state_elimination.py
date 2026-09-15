import random

from reasoning_core.tasks.generated.k3_invariants_r1.gnfa_state_elimination.gnfa_state_elimination import (
    GnfaStateElimination,
    NONE,
    union,
    concat,
    star,
)


def _task(level=0, mode="final"):
    t = GnfaStateElimination()
    cfg = t.config_cls()
    cfg.apply_difficulty(level)
    t.config = cfg
    return t


def test_union_basic():
    assert union("a", "b") == "(a)|(b)"
    assert union("a", NONE) == "a"
    assert union(NONE, "b") == "b"
    assert union("a", "a") == "a"
    assert union(NONE, NONE) == NONE


def test_concat_basic():
    assert concat("a", "b") == "ab"
    assert concat("a", "eps") == "a"
    assert concat(NONE, "b") == NONE
    assert concat("a", "bc") == "abc"


def test_star_basic():
    assert star("eps") == "eps"
    assert star("a") == "a*"
    assert star("ab") == "(ab)*"
    assert star("(a)|(b)") == "((a)|(b))*"
    assert star(NONE) == "eps"
    assert star("ab*") == "(ab*)*"


def test_generates_and_scores_roundtrip():
    random.seed(42)
    for level in (0, 6):
        t = _task(level=level)
        for _ in range(20):
            e = t.generate_entry()
            assert isinstance(e.answer, str)
            assert t.score_answer(e.answer, e) == 1.0


def test_scorer_rejects_garbage():
    random.seed(7)
    for level in (0, 6):
        t = _task(level=level)
        for _ in range(10):
            e = t.generate_entry()
            assert t.score_answer("", e) < 1.0
            assert t.score_answer("garbage", e) < 1.0
            assert t.score_answer(None, e) < 1.0
            assert t.score_answer("x", e) < 1.0


def test_difficulty_changes_state_count():
    random.seed(1)
    t0 = _task(level=0)
    t6 = _task(level=6)
    assert t6.config.state_count > t0.config.state_count


def test_reproducible_under_seed():
    random.seed(99)
    a = [_task(level=3).generate_entry().answer for _ in range(5)]
    random.seed(99)
    b = [_task(level=3).generate_entry().answer for _ in range(5)]
    assert a == b
