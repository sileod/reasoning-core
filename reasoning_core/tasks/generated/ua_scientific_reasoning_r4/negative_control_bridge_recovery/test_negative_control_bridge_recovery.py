"""Tests for the negative-control bridge recovery task."""

import random

import numpy as np

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.negative_control_bridge_recovery.negative_control_bridge_recovery import (
    NegativeControlBridgeRecovery,
)


def _solve_from_prompt(metadata):
    """Independently solve the bridge from the displayed data, as a reader would."""
    K = np.array(metadata["K_rows"], dtype=float)
    ey = np.array(metadata["ey"], dtype=float)
    pz = np.array(metadata["pz"], dtype=float)
    rank = int(np.linalg.matrix_rank(K))
    if rank < len(pz):
        return "nonidentifiable"
    h, *_ = np.linalg.lstsq(K, ey, rcond=None)
    return f"{float(np.dot(h, pz)):.3f}"


def test_example_scores_gold():
    task = NegativeControlBridgeRecovery()
    for level in (0, 2, 5):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_prompt_reproduces_answer():
    task = NegativeControlBridgeRecovery()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(40):
            ex = task.generate_example()
            recomputed = _solve_from_prompt(ex.metadata)
            if recomputed == "nonidentifiable":
                assert ex.answer == "nonidentifiable"
            else:
                r = float(recomputed)
                g = float(ex.answer)
                assert abs(r - g) <= 0.5e-2, (level, recomputed, ex.answer)


def test_identifiable_answers_are_in_domain():
    task = NegativeControlBridgeRecovery()
    task.config.set_level(6)
    for _ in range(60):
        ex = task.generate_example()
        if ex.answer != "nonidentifiable":
            assert -5.01 <= float(ex.answer) <= 5.01


def test_both_answer_regimes_present():
    task = NegativeControlBridgeRecovery()
    seen_nonident = seen_num = False
    for _ in range(400):
        ex = task.generate_example()
        if ex.answer == "nonidentifiable":
            seen_nonident = True
        else:
            seen_num = True
        if seen_nonident and seen_num:
            break
    assert seen_nonident and seen_num


def test_junk_and_wrong_answers_rejected():
    task = NegativeControlBridgeRecovery()
    for level in (0, 5):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            for bad in ("", "reajrjrje9595!", "__import__('os')"):
                if bad != ex.answer:
                    assert task.score_answer(bad, ex) < 1.0
            if ex.answer != "nonidentifiable":
                assert task.score_answer("nonidentifiable", ex) < 1.0
            elif ex.answer == "nonidentifiable":
                assert task.score_answer("0.000", ex) < 1.0


def test_level_changes_config():
    task = NegativeControlBridgeRecovery()
    task.config.set_level(0)
    c0 = task.config.kz
    task.config.set_level(6)
    assert task.config.kz > c0


def test_metadata_json_serializable():
    import json

    task = NegativeControlBridgeRecovery()
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))
