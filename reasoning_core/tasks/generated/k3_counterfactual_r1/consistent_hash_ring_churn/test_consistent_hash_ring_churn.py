import json
import random

from reasoning_core.tasks.generated.k3_counterfactual_r1.consistent_hash_ring_churn.consistent_hash_ring_churn import (
    ConsistentHashRingChurn,
    _parse_answer,
    _successor,
)


def test_generate_and_score():
    task = ConsistentHashRingChurn()
    for _ in range(20):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_parse_roundtrip():
    task = ConsistentHashRingChurn()
    for _ in range(10):
        entry = task.generate_example()
        parsed = _parse_answer(entry.answer)
        assert parsed is not None


def test_answer_determines_moves():
    task = ConsistentHashRingChurn()
    for _ in range(20):
        entry = task.generate_example()
        meta = entry.metadata
        final = meta["final_nodes"]
        initial = meta["initial_nodes"]
        for (lo, hi, per) in meta["moved_ranges"]:
            assert len(per) > 0
            for (p, cur, new) in per:
                assert _successor(p, final) == new
                assert _successor(p, initial) == cur
        for (lo, hi, owner) in meta["unchanged_ranges"]:
            for p in range(lo, hi):
                assert _successor(p, final) == _successor(p, initial) == owner


def test_wrong_answer_scores_zero():
    task = ConsistentHashRingChurn()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0


def test_final_nodes_nonempty_every_level():
    task = ConsistentHashRingChurn()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(50):
            entry = task.generate_example()
            assert len(entry.metadata["final_nodes"]) >= 1
            assert len(entry.metadata["initial_nodes"]) >= 1
            assert task.score_answer(entry.answer, entry) == 1.0


def test_metadata_json_serializable():
    task = ConsistentHashRingChurn()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_example()
            json.dumps(entry.metadata.to_dict() if hasattr(entry.metadata, "to_dict") else dict(entry.metadata))


def test_replay_events_matches_final():
    task = ConsistentHashRingChurn()
    for _ in range(20):
        entry = task.generate_example()
        meta = entry.metadata
        working = set(meta["initial_nodes"])
        for (action, node) in meta["events"]:
            if action == "join":
                working.add(node)
            else:
                working.remove(node)
        assert sorted(working) == meta["final_nodes"]


def test_difficulty_increases_structure():
    task = ConsistentHashRingChurn()
    task.config.set_level(0)
    l0 = task.config.num_keys + task.config.num_joins + task.config.num_failures + task.config.num_initial_nodes
    task.config.set_level(6)
    l6 = task.config.num_keys + task.config.num_joins + task.config.num_failures + task.config.num_initial_nodes
    assert l6 > l0
