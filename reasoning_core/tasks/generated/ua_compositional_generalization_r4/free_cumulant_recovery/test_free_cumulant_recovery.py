import random

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.free_cumulant_recovery.free_cumulant_recovery import (
    FreeCumulantRecovery,
    _moment,
)


def test_contract_roundtrip():
    task = FreeCumulantRecovery()
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = FreeCumulantRecovery()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0
    assert task.score_answer("import os", ex) == 0.0


def test_metadata_json_roundtrip():
    import json

    task = FreeCumulantRecovery()
    for _ in range(20):
        ex = task.generate_example()
        wire = json.loads(json.dumps(dict(ex.metadata)))
        assert wire["answer"] == int(ex.answer)


def test_levels_change_config():
    task = FreeCumulantRecovery()
    task.config.set_level(0)
    lo = task.config.max_order
    task.config.set_level(6)
    hi = task.config.max_order
    assert hi > lo


def test_moment_scalar_small():
    # m_1 = k1 ; m_2 = k2 + k1^2 ; m_3 = k3 + 3 k1 k2 + k1^3
    k = {1: 2, 2: 3, 3: 1}
    assert _moment(("X",), {"X": [k[1]]}) == 2
    assert _moment(("X", "X"), {"X": [k[1], k[2]]}) == 3 + 4
    kby = {"X": [2, 3, 1]}
    assert _moment(("X", "X", "X"), kby) == 1 + 3 * 2 * 3 + 8


def test_mixed_block_mixing_zero():
    # m_AB = kA1 * kB1 (singletons only)
    kby = {"A": [2, 3], "B": [5, 7]}
    assert _moment(("A", "B"), kby) == 2 * 5
    # m_AA = kA2 + kA1^2
    assert _moment(("A", "A"), kby) == 3 + 4


def test_answer_not_present_in_prompt():
    import re

    task = FreeCumulantRecovery()
    for _ in range(30):
        ex = task.generate_example()
        vals = set(re.findall(r"=\s*(-?\d+)", ex.prompt))
        assert ex.answer not in vals, (ex.answer, ex.prompt)


def test_deterministic():
    random.seed(7)
    t1 = FreeCumulantRecovery()
    a1 = [t1.generate_example().answer for _ in range(5)]
    random.seed(7)
    t2 = FreeCumulantRecovery()
    a2 = [t2.generate_example().answer for _ in range(5)]
    assert a1 == a2
