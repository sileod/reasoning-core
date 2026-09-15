import random

from reasoning_core.tasks.generated.k3_representation_specific_r1.stone_placement_capture.stone_placement_capture import (
    StoneCaptureConfig,
    StonePlacementCapture,
    _calculate_answer,
    _group_from,
)


def _task(level):
    task = StonePlacementCapture()
    task.config = StoneCaptureConfig()
    task.config.set_level(level)
    return task


def test_gold_scores_one():
    for level in (0, 2, 5, 6):
        t = _task(level)
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_bad_answers_fail():
    random.seed(1)
    t = _task(0)
    e = t.generate_example()
    assert t.score_answer("", e) == 0.0
    assert t.score_answer("garbage", e) == 0.0


def test_computes_captured_matches():
    random.seed(2)
    for _ in range(30):
        t = _task(0)
        e = t.generate_example()
        m = e.metadata
        assert 0 <= m["num_captured"]
        assert 0 <= m["num_released"]
        assert m["num_captured"] > 0 or m["num_released"] > 0
        board = [row[:] for row in m["board"]]
        cap, rem, relib, adj = _calculate_answer(board, tuple(m["stone"]), m["color"], m["size"])
        assert len(cap) == m["num_captured"]
        assert len(relib) == m["num_released"]


def test_answer_reconstructable():
    random.seed(4)
    for _ in range(20):
        t = _task(3)
        e = t.generate_example()
        parts = e.answer.split("; ")
        assert e.metadata["num_captured"] > 0
        assert parts[0] == f"captured={e.metadata['num_captured']}"


def test_metadata_json_serializable():
    import json

    random.seed(3)
    t = _task(2)
    e = t.generate_example()
    json.dumps(e.metadata)


def test_difficulty_changes():
    t = _task(0)
    t6 = _task(6)
    assert t.config.size != t6.config.size
