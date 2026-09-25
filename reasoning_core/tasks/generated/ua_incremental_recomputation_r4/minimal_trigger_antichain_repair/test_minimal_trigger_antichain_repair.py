import random

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.minimal_trigger_antichain_repair.minimal_trigger_antichain_repair import (
    MinimalTriggerAntichainRepair,
    _antichain,
    _canonical,
    _split_answer,
    _parse_antichain,
)


def test_gold_scores_one():
    random.seed(7)
    task = MinimalTriggerAntichainRepair()
    for _ in range(60):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    task = MinimalTriggerAntichainRepair()
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("garbage", e) < 1.0
    assert task.score_answer("reajrjrje9595!", e) < 1.0


def test_repair_is_consistent_with_metadata():
    random.seed(3)
    task = MinimalTriggerAntichainRepair()
    for _ in range(60):
        e = task.generate_example()
        meta = e.metadata
        original = {frozenset(ss) for ss in meta["original"]}
        repaired = {frozenset(ss) for ss in meta["repaired"]}
        added = {frozenset(ss) for ss in meta["added"]}
        removed = {frozenset(ss) for ss in meta["removed"]}
        assert added == {x for x in repaired if x not in original}
        assert removed == {x for x in original if x not in repaired}
        assert (added | removed) != set()
        parsed = _split_answer(e.answer)
        assert parsed is not None
        assert parsed == (added, removed)


def test_all_levels_generate():
    random.seed(11)
    for level in range(7):
        task = MinimalTriggerAntichainRepair()
        task.config.set_level(level)
        for _ in range(10):
            e = task.generate_entry()
            assert task.score_answer(e.answer, e) == 1.0


def test_difficulty_changes():
    c = MinimalTriggerAntichainRepair().config_cls()
    base = c.sources
    c.apply_difficulty(6)
    assert c.sources > base
    c.apply_difficulty(0)
    assert c.sources <= base


def test_answer_not_on_surface():
    random.seed(5)
    task = MinimalTriggerAntichainRepair()
    for _ in range(40):
        e = task.generate_example()
        assert e.answer not in e.prompt


def test_antichain_reference():
    s = 3
    target = 4
    # gate3 = OR(A,B); target = AND(gate3, C) -> triggers {A,C} and {B,C}
    spec = {3: ((0, 1), 1), 4: ((3, 2), 2)}
    got = _antichain(spec, s, target)
    assert got == {frozenset({0, 2}), frozenset({1, 2})}


def test_canonical_is_sorted_deterministic():
    ac = {frozenset({2}), frozenset({0, 1})}
    assert _canonical(ac) == "A,B;C"
    assert _canonical(set()) == "-"
    assert _parse_antichain("-") == set()


def test_empty_collection_in_middle_parses():
    assert _split_answer("ADDED: -; REMOVED: A,B") == (set(),
                                                       {frozenset({0, 1})})
    assert _split_answer("ADDED: A,B; REMOVED: -") == ({frozenset({0, 1})},
                                                       set())
    assert _split_answer("ADDED: -; REMOVED: -") == (set(), set())
    assert _split_answer("yes") is None


def test_all_three_edit_types_occur():
    random.seed(19)
    task = MinimalTriggerAntichainRepair()
    seen = set()
    for _ in range(200):
        seen.add(task.generate_example().metadata["edit_type"])
        if len(seen) == 3:
            break
    assert seen == {"gate", "threshold", "shared"}


def test_edited_network_recomputes_to_repaired():
    from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.minimal_trigger_antichain_repair.minimal_trigger_antichain_repair import (
        _write_network,
    )
    random.seed(23)
    for _ in range(40):
        e = MinimalTriggerAntichainRepair().generate_example()
        meta = e.metadata
        s = int(meta["sources"])
        m = int(meta["gates"])
        spec = {}
        for k in range(m):
            parents, th = meta["base_gate_spec"][str(k)]
            spec[s + k] = (tuple(parents), th)
        target = s + m
        base = _write_network(dict(spec), s, m, target, meta["target_threshold"], None)
        orig = {frozenset(ss) for ss in meta["original"]}
        assert orig == _antichain(base, s, target)


def test_repair_changes_antichain():
    random.seed(29)
    for _ in range(30):
        e = MinimalTriggerAntichainRepair().generate_example()
        meta = e.metadata
        assert {frozenset(ss) for ss in meta["original"]} != {
            frozenset(ss) for ss in meta["repaired"]
        }

