import random

from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.epoch_retirement_safety.epoch_retirement_safety import (
    EpochRetirementSafety,
)


def test_generate_and_score_roundtrip():
    task = EpochRetirementSafety()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(30):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0
            assert task.score_answer("", entry) < 1.0
            assert task.score_answer("garbage nonsense", entry) < 1.0


def test_threshold_semantics():
    task = EpochRetirementSafety()
    task.config.set_level(0)
    for _ in range(50):
        entry = task.generate_example()
        m = entry.metadata
        oldest = m["oldest_reader"]
        threshold = oldest + m["grace"]
        assert m["threshold"] == threshold
        assert sorted(m["safe"]) == [o for o, e in m["retired"].items() if e < threshold]
        assert sorted(m["blocked"]) == [o for o, e in m["retired"].items() if e >= threshold]


def test_balanced_labels():
    task = EpochRetirementSafety()
    task.config.set_level(0)
    counts = {"yes": 0, "no": 0}
    for _ in range(500):
        entry = task.generate_example()
        m = entry.metadata
        if m["ask"] == "yesno":
            counts[entry.answer] += 1
    assert counts["yes"] > 40 and counts["no"] > 40


def test_metadata_json_serializable():
    import json

    task = EpochRetirementSafety()
    for level in (0, 5):
        task.config.set_level(level)
        entry = task.generate_example()
        json.dumps(entry.metadata)
