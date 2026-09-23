import random

from reasoning_core.tasks.generated.k3_multi_relation_integration_r4.match_clear_cascade_resolution.match_clear_cascade_resolution import (
    _norm,
    _simulate,
    MatchClearCascadeResolver,
)


def test_roundtrip_score():
    task = MatchClearCascadeResolver()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    task = MatchClearCascadeResolver()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("not a board", x) < 1.0


def test_cascade_matches_gold():
    task = MatchClearCascadeResolver()
    for _ in range(5):
        x = task.generate_example()
        m = x.metadata
        final, _, ok = _simulate(_swapped(m), m["rows"], m["cols"], m["stream"], 200)
        assert ok and final == m["final_board"]


def _swapped(m):
    board = list(m["board"])
    (r1, c1), (r2, c2) = m["swap"]
    cols = m["cols"]
    board[r1 * cols + c1], board[r2 * cols + c2] = board[r2 * cols + c2], board[r1 * cols + c1]
    return "".join(board)


def test_difficulty_changes_config():
    task = MatchClearCascadeResolver()
    task.config.set_level(0)
    l0 = (task.config.rows, task.config.cols)
    task.config.set_level(6)
    l6 = (task.config.rows, task.config.cols)
    assert l6[0] * l6[1] > l0[0] * l0[1]


def test_generation_all_levels():
    task = MatchClearCascadeResolver()
    for lvl in range(7):
        task.config.set_level(lvl)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_norm():
    assert _norm("AB C.D") == "ABCD"
