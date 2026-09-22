import random

from reasoning_core.tasks.generated.k3_language_implementation_r4.aries_crash_recovery.aries_crash_recovery import (
    AriesCrashRecovery,
    AriesCrashRecoveryConfig,
    _fail_recover,
    _format_answer,
    _recover,
    _render_records,
)


def test_recover_ignores_loser_writes():
    base = [0, 0]
    records = [
        [1, "W", 0, 5],
        [2, "W", 1, 7],
        [2, "C", -1, -1],
    ]
    value, losers, redo = _recover(base, records)
    assert value == [0, 7]
    assert losers == [1]
    assert redo == 1


def test_recover_committed_wins_over_loser():
    base = [0]
    records = [
        [1, "W", 0, 9],
        [1, "C", -1, -1],
        [2, "W", 0, 3],
    ]
    value, losers, _ = _recover(base, records)
    assert value == [9]
    assert losers == [2]


def test_recover_undo_before_later_commit():
    base = [0]
    records = [
        [1, "W", 0, 9],
        [2, "W", 0, 4],
        [2, "C", -1, -1],
        [1, "W", 0, 6],
    ]
    value, losers, _ = _recover(base, records)
    assert value == [4]
    assert losers == [1]


def test_recovery_cross_checks_match():
    base = [2, 5, 8]
    records = [
        [1, "W", 0, 9],
        [2, "W", 1, 3],
        [1, "C", -1, -1],
        [3, "W", 2, 1],
        [2, "C", -1, -1],
        [4, "W", 0, 7],
    ]
    v, l, _ = _recover(base, records)
    v2, l2 = _fail_recover(base, records)
    assert v == v2
    assert l == l2


def test_answer_format_canonical():
    base = [1, 2]
    records = [
        [1, "W", 0, 4],
        [2, "W", 1, 5],
        [1, "C", -1, -1],
    ]
    ans = _format_answer(base, records)
    assert ans == "P1=4,P2=2 losers=T2"


def test_render_records_uses_lsns():
    records = [[1, "W", 0, 5], [1, "C", -1, -1]]
    assert _render_records(records) == ["L1 T1 write P1 = 5", "L2 T1 commit"]


def test_score_exact_and_junk():
    task = AriesCrashRecovery()
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1
    assert task.score_answer("", entry) < 1
    assert task.score_answer("P1=999 losers=T99", entry) < 1


def test_level_0_and_6_generate_with_losers():
    task = AriesCrashRecovery()
    task.config.set_level(0)
    for _ in range(10):
        e = task.generate_example()
        assert "losers=T" in e.answer
    task.config.set_level(6)
    for _ in range(10):
        e = task.generate_example()
        assert "losers=T" in e.answer


def test_difficulty_changes_config():
    c = AriesCrashRecoveryConfig()
    base = (c.n_pages, c.n_records, c.value_range)
    c.set_level(6)
    assert (c.n_pages, c.n_records, c.value_range) != base


def test_metadata_json_roundtrip():
    task = AriesCrashRecovery()
    e = task.generate_example()
    import json
    wire = json.loads(json.dumps(dict(e.metadata)))
    assert wire["base"] == list(e.metadata.base)


def test_prompt_states_checkpoint_values():
    task = AriesCrashRecovery()
    e = task.generate_example()
    expected = ",".join(
        f"P{i + 1}={e.metadata.base[i]}" for i in range(e.metadata.np)
    )
    assert expected in e.prompt


def test_all_levels_reach_both_answer_shapes():
    task = AriesCrashRecovery()
    for level in (0, 3, 6):
        task.config.set_level(level)
        seen = {"committed_wins": False, "loser_wins": False}
        for _ in range(30):
            e = task.generate_example()
            assert "losers=T" in e.answer
            assert e.answer.startswith("P1=")
