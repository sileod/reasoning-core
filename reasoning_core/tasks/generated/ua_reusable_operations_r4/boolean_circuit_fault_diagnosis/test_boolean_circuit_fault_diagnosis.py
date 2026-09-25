import random

import pytest

from reasoning_core.tasks.generated.ua_reusable_operations_r4.boolean_circuit_fault_diagnosis.boolean_circuit_fault_diagnosis import (
    BooleanCircuitFaultDiagnosis,
)


@pytest.fixture(scope="module")
def task():
    return BooleanCircuitFaultDiagnosis()


def test_roundtrip_and_scoring(task):
    for level in (0, 3, 6):
        t = BooleanCircuitFaultDiagnosis()
        t.config.set_level(level)
        for _ in range(15):
            ex = t.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_both_modes_emerge(task):
    modes = set()
    t = BooleanCircuitFaultDiagnosis()
    for _ in range(60):
        ex = t.generate_example()
        modes.add(ex.metadata.mode)
    assert 'diag' in modes and 'detect' in modes


def test_diag_answer_reproduces_observed(task):
    from reasoning_core.tasks.generated.ua_reusable_operations_r4.boolean_circuit_fault_diagnosis.boolean_circuit_fault_diagnosis import (
        _sim, _unique_min_diagnosis,
    )
    t = BooleanCircuitFaultDiagnosis()
    for _ in range(40):
        ex = t.generate_example()
        if ex.metadata.mode != 'diag':
            continue
        m = ex.metadata
        assert [int(x) for x in ex.answer.split()] == m.faulty
        assert ex.answer.split() == sorted(ex.answer.split(), key=int)
        # the injected faults reproduce the observed outputs
        got = _sim(len(m.inputs), m.gate_ops, m.gate_ins, m.inputs,
                   [(f[0], f[1]) for f in m.faults])
        assert [got[o] for o in m.outputs] == m.observed
        # the answer is the unique minimal diagnosis among internal gates
        out_set = set(m.outputs)
        n_in = len(m.inputs)
        cand = sorted(n for n in range(n_in, n_in + len(m.gate_ops)) if n not in out_set)
        diag = _unique_min_diagnosis(n_in, m.gate_ops, m.gate_ins,
                                     m.inputs, m.outputs, m.observed, len(m.faulty), cand)
        assert diag == m.faulty


def test_detect_answer_is_yes_no(task):
    t = BooleanCircuitFaultDiagnosis()
    for _ in range(30):
        ex = t.generate_example()
        if ex.metadata.mode != 'detect':
            continue
        assert ex.answer in ('YES', 'NO')
        assert ex.metadata.observed != ex.metadata.expected if ex.answer == 'YES' else ex.metadata.observed == ex.metadata.expected


def test_junk_and_empty_score_zero(task):
    t = BooleanCircuitFaultDiagnosis()
    ex = t.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("garbage words here", ex) < 1.0
    assert task.score_answer("not-an-answer", ex) < 1.0


def test_deterministic_under_seed():
    a = []
    for seed in (0, 0):
        random.seed(seed)
        t = BooleanCircuitFaultDiagnosis()
        ex = t.generate_example()
        a.append((ex.answer, t.render_prompt(ex.metadata)))
    assert a[0] == a[1]


def test_balanced_binary(task):
    t = BooleanCircuitFaultDiagnosis()
    yes = no = 0
    for _ in range(80):
        ex = t.generate_example()
        if ex.metadata.mode == 'detect':
            if ex.answer == 'YES':
                yes += 1
            else:
                no += 1
    assert yes > 0 and no > 0
