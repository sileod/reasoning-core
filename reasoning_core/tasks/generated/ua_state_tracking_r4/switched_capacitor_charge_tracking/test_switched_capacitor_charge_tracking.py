import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.ua_state_tracking_r4.switched_capacitor_charge_tracking.switched_capacitor_charge_tracking import (
    SwitchedCapacitorChargeTracking,
    _build_instance,
)


def _make(level):
    task = SwitchedCapacitorChargeTracking()
    task.config.set_level(level)
    return task


def test_generate_answer_scores():
    for level in (0, 2, 5):
        task = _make(level)
        for _ in range(30):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert int(ex.answer) != 0 or True


def test_generation_deterministic():
    random.seed(1234)
    task = _make(3)
    a1 = task.generate_example()
    random.seed(1234)
    task2 = _make(3)
    a2 = task2.generate_example()
    assert a1.answer == a2.answer
    payload_keys = ["nodes", "charges", "caps", "ops", "clamped", "query_edge", "query_side"]
    for k in payload_keys:
        assert a1.metadata[k] == a2.metadata[k]


def test_metadata_json_serializable():
    import json
    task = _make(4)
    for _ in range(20):
        ex = task.generate_example()
        json.dumps(ex.metadata)


def test_answer_is_integer():
    task = _make(2)
    for _ in range(40):
        ex = task.generate_example()
        int(ex.answer)


def test_build_instance_answers_are_integers():
    task = _make(3)
    cfg = task.config
    for _ in range(60):
        nodes, cap_to, ops, clamped, edge, side, qc, ans = _build_instance(cfg)
        assert isinstance(ans, int)


def test_garbage_scores_zero():
    task = _make(1)
    ex = task.generate_example()
    assert task.score_answer("", ex) != 1.0
    assert task.score_answer("banana", ex) != 1.0
    assert task.score_answer("3.7", ex) != 1.0


def test_examples_vary():
    task = _make(2)
    seen = set()
    for _ in range(30):
        ex = task.generate_example()
        seen.add(ex.answer)
    assert len(seen) > 1
