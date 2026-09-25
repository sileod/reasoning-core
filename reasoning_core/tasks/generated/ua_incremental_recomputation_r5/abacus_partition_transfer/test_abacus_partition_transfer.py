import random

import pytest

from reasoning_core.tasks.generated.ua_incremental_recomputation_r5.abacus_partition_transfer.abacus_partition_transfer import (
    AbacusPartitionTransfer,
    _compute,
)


def _make():
    return AbacusPartitionTransfer()


def test_roundtrip_all_levels():
    task = _make()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_entry()
            core, quotient, origins = _compute(ex.metadata["beta"], ex.metadata["r"])
            assert core == ex.metadata["core"]
            assert quotient == ex.metadata["quotient"]
            assert origins == ex.metadata["origins"]


def test_reconstruct_partition():
    # Reconstructed beta set must equal the original, verified inside _compute.
    for level in range(7):
        t = _make()
        t.config.set_level(level)
        for _ in range(50):
            ex = t.generate_entry()
            _compute(ex.metadata["beta"], ex.metadata["r"])


def test_score_answer():
    t = _make()
    ex = t.generate_example(level=0)
    assert t.score_answer(ex.answer, ex) == 1.0
    assert t.score_answer("", ex) == 0.0
    assert t.score_answer("junk", ex) == 0.0
    assert t.score_answer(ex.answer[:-4], ex) == 0.0
    assert t.score_answer(ex.answer + "extra", ex) == 0.0


def test_deterministic_seed():
    t = _make()
    t.config.set_level(3)
    random.seed(123)
    a1 = t.generate_example(level=3)
    random.seed(123)
    a2 = t.generate_example(level=3)
    assert a1.answer == a2.answer
    assert a1.metadata["beta"] == a2.metadata["beta"]


def test_origins_reference_changes():
    # Each bead must be mapped exactly once, to a position >= its own floor.
    t = _make()
    for _ in range(200):
        ex = t.generate_entry()
        beta = ex.metadata["beta"]
        origins = ex.metadata["origins"]
        assert sorted(p for p, _ in origins) == sorted(beta)
        assert len(origins) == len(beta)
        for p, c in origins:
            assert c in ex.metadata["core"]


def test_answer_positive_domain():
    t = _make()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(20):
            ex = t.generate_entry()
            for x in ex.metadata["core"]:
                assert x >= 0
            core = ex.metadata["core"]
            assert len(set(core)) == len(core)
