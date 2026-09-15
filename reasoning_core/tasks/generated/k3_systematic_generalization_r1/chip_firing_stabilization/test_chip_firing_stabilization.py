import random

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.chip_firing_stabilization.chip_firing_stabilization import (
    ChipFiringStabilization,
    _stabilize,
    _is_stable,
    _normalize,
)


def test_gold_scores_one():
    task = ChipFiringStabilization()
    for _ in range(50):
        x = task.generate_entry()
        assert task.score_answer(x.answer, x) == 1.0


def test_metadata_json_serializable():
    import json
    task = ChipFiringStabilization()
    for _ in range(20):
        x = task.generate_entry()
        json.dumps(x.metadata)


def test_stabilization_is_stable():
    task = ChipFiringStabilization()
    for _ in range(50):
        x = task.generate_entry()
        assert _is_stable(x.metadata["adj"], x.metadata["stable"])


def test_firing_conserves_chips():
    task = ChipFiringStabilization()
    for _ in range(50):
        x = task.generate_entry()
        assert sum(x.metadata["stable"]) == sum(x.metadata["chips"])


def test_sequence_fires_out():
    task = ChipFiringStabilization()
    for _ in range(100):
        x = task.generate_entry()
        n = x.metadata["n"]
        deg = [len(a) for a in x.metadata["adj"]]
        for v in range(n):
            assert x.metadata["stable"][v] < deg[v]


def test_normalize():
    assert _normalize("[1, 2, 3]") == (1, 2, 3)
    assert _normalize("1 2 3") == (1, 2, 3)
    assert _normalize("garbage") is None
    assert _normalize(None) is None


def test_garbage_scores_zero():
    task = ChipFiringStabilization()
    x = task.generate_entry()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer(None, x) == 0.0


def test_levels_vary():
    task = ChipFiringStabilization()
    for level in range(7):
        task.config.set_level(level)
        x = task.generate_entry()
        assert task.score_answer(x.answer, x) == 1.0


def test_deterministic_seed():
    task = ChipFiringStabilization()
    task.config.set_level(3)
    random.seed(42)
    e1 = task.generate_entry().answer
    random.seed(42)
    e2 = task.generate_entry().answer
    assert e1 == e2
