"""Tests for the registration-waitlist-replay task."""

import random

from reasoning_core.tasks.generated.k3_non_local_structured_r4.registration_waitlist_replay.registration_waitlist_replay import (
    RegistrationWaitlistReplay,
    _add,
    _drop,
    _swap,
    _parse_roster,
)


def _replay(metadata):
    sections = metadata["sections"]
    caps = {sec: cap for sec, cap in zip(sections, metadata["caps"])}
    seated = {sec: list(r) for sec, r in zip(sections, metadata["init_roster"])}
    wait = {sec: list(w) for sec, w in zip(sections, metadata["init_wait"])}
    for op in metadata["ops"]:
        if op[0] == "add":
            _add(seated, wait, caps, op[2], op[1])
        elif op[0] == "drop":
            _drop(seated, wait, caps, op[2], op[1])
        else:
            _swap(seated, wait, op[1], op[2], op[3], op[4])
    for sec in sections:
        assert len(seated[sec]) <= caps[sec]
        assert len(set(seated[sec])) == len(seated[sec])
        assert len(set(wait[sec])) == len(wait[sec])
    occupied = []
    for sec in sections:
        occupied.extend(seated[sec])
        occupied.extend(wait[sec])
    assert len(set(occupied)) == len(occupied), "a student appears more than once"
    return seated, wait


def test_config_scales():
    t = RegistrationWaitlistReplay()
    base = t.config.n_ops
    t.config.set_level(0)
    lo = t.config.n_ops
    t.config.set_level(6)
    hi = t.config.n_ops
    assert lo <= hi
    assert hi > base


def test_gold_scores_one_all_modes():
    t = RegistrationWaitlistReplay()
    seen = set()
    for _ in range(200):
        entry = t.generate_example()
        assert t.score_answer(entry.answer, entry) == 1.0
        seen.add(entry.metadata["mode"])
    assert {"roster", "outcome", "waitsize"} <= seen


def test_junk_scores_zero():
    t = RegistrationWaitlistReplay()
    for _ in range(60):
        entry = t.generate_example()
        assert t.score_answer("", entry) < 1.0
        assert t.score_answer("reajrjrje9595!", entry) < 1.0
        assert t.score_answer("   ", entry) < 1.0


def test_generation_survives_all_levels():
    t = RegistrationWaitlistReplay()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(5):
            entry = t.generate_example()
            assert t.score_answer(entry.answer, entry) == 1.0


def test_roster_canonical_and_reproducible():
    t = RegistrationWaitlistReplay()
    random.seed(12345)
    a = [t.generate_example().answer for _ in range(10)]
    random.seed(12345)
    b = [t.generate_example().answer for _ in range(10)]
    assert a == b


def test_promotion_cascade():
    seated = {"A": ["s1", "s2"]}
    wait = {"A": ["s3"]}
    caps = {"A": 2}
    _drop(seated, wait, caps, "A", "s1")
    assert seated["A"] == ["s2", "s3"]
    assert wait["A"] == []


def test_swap_exchanges_status():
    seated = {"A": ["s1"], "B": []}
    wait = {"A": [], "B": ["s2"]}
    _swap(seated, wait, "s1", "A", "s2", "B")
    assert sorted(seated["A"] + wait["A"]) == ["s2"]
    assert sorted(seated["B"] + wait["B"]) == ["s1"]
    assert seated["B"] == []


def test_parse_roster():
    assert _parse_roster("A:[s1,s3]; B:[s2]") == {
        "A": ["s1", "s3"],
        "B": ["s2"],
    }
    assert _parse_roster("A:[s3, s1]") == {"A": ["s1", "s3"]}


def test_state_invariants_hold():
    from reasoning_core.tasks.generated.k3_non_local_structured_r4.registration_waitlist_replay.registration_waitlist_replay import _roster_answer

    t = RegistrationWaitlistReplay()
    for level in (0, 2, 5):
        t.config.set_level(level)
        for _ in range(50):
            entry = t.generate_example()
            seated, wait = _replay(entry.metadata)
            mode = entry.metadata["mode"]
            if mode == "roster":
                assert _roster_answer(seated, entry.metadata["sections"]) == entry.answer
            elif mode == "outcome":
                target = entry.metadata["target"]
                sec, slot = None, None
                for s in entry.metadata["sections"]:
                    if target in seated[s]:
                        sec, slot = s, "seated"
                    elif target in wait[s]:
                        sec, slot = s, "wait"
                if sec is None:
                    assert entry.answer == "not enrolled"
                else:
                    assert entry.answer == f"{slot} in {sec}"
            else:
                target = entry.metadata["target"]
                assert int(entry.answer) == len(wait[target])
