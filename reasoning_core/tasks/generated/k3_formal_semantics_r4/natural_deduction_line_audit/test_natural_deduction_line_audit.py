import random

from reasoning_core.tasks.generated.k3_formal_semantics_r4.natural_deduction_line_audit.natural_deduction_line_audit import (
    NaturalDeductionLineAudit,
)


def test_roundtrip():
    task = NaturalDeductionLineAudit()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_junk():
    task = NaturalDeductionLineAudit()
    for _ in range(10):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("garbage here", ex) == 0.0


def test_balanced_answers():
    task = NaturalDeductionLineAudit()
    labeled = 0
    valid = 0
    for _ in range(40):
        ex = task.generate_example()
        labeled += 1
        if ex.answer.strip().upper() == "VALID":
            valid += 1
    assert 0 < valid < labeled


def test_difficulty_changes():
    task = NaturalDeductionLineAudit()
    base = dict((k, v) for k, v in task.config.__dict__.items())
    task.config.set_level(6)
    hi = dict((k, v) for k, v in task.config.__dict__.items())
    assert base != hi
    assert hi["max_steps"] > base["max_steps"]
    assert hi["max_premises"] > base["max_premises"]


def test_deterministic():
    random.seed(1259343118)
    task = NaturalDeductionLineAudit()
    a = [task.generate_example().answer for _ in range(10)]
    random.seed(1259343118)
    task2 = NaturalDeductionLineAudit()
    b = [task2.generate_example().answer for _ in range(10)]
    assert a == b
