import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.partial_identification_bounds.partial_identification_bounds import (
    PartialIdentificationBounds,
    TASK_META,
)


def test_summary_and_meta():
    assert "partial_identification_bounds (variant 2 of 3)" in TASK_META["idea"]
    assert TASK_META["hypothesis"] == "P010"
    assert "monotone" in PartialIdentificationBounds.summary


def test_generation_and_scoring_all_modes():
    task = PartialIdentificationBounds()
    seen = set()
    for _ in range(200):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        seen.add(entry.metadata["mode"])
    assert seen == {"none", "monotone", "instrument"}


def test_bounds_domain():
    task = PartialIdentificationBounds()
    for _ in range(300):
        entry = task.generate_example()
        low, high = (float(x) for x in entry.answer.split(","))
        assert low <= high, entry.answer
        assert -1.0 <= low <= 1.0
        assert -1.0 <= high <= 1.0


def test_empty_and_junk_answers():
    task = PartialIdentificationBounds()
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("garbage", entry) < 1.0
    assert task.score_answer("not, a, number", entry) < 1.0


def test_difficulty_changes_config():
    task = PartialIdentificationBounds()
    task.config.set_level(0)
    c0 = task.config.level
    task.config.set_level(6)
    assert task.config.level == 6
    assert c0 == 0


def test_metadata_json_serializable():
    import json

    task = PartialIdentificationBounds()
    for _ in range(50):
        entry = task.generate_example()
        json.dumps(entry.metadata)


def test_label_balance_nonextreme():
    task = PartialIdentificationBounds()
    lows = []
    for _ in range(400):
        entry = task.generate_example()
        low = float(entry.answer.split(",")[0])
        lows.append(low)
    distinct = len(set(round(x, 2) for x in lows))
    assert distinct >= 6
