import random

from reasoning_core.tasks.generated.wave12.transaction_serializability.transaction_serializability import (
    TransactionSerializability,
    analyze,
)


def test_gold_answers_score_one():
    t = TransactionSerializability()
    for _ in range(200):
        ex = t.generate_example()
        assert t.score_answer(ex.answer, ex) == 1.0


def test_wrong_and_junk_do_not_score_one():
    t = TransactionSerializability()
    for _ in range(200):
        ex = t.generate_example()
        assert t.score_answer("", ex) < 1.0
        assert t.score_answer("junk", ex) < 1.0
        serializable = ex.metadata["serializable"]
        if serializable:
            other = ex.metadata["serial_order"]
            # perturbation: a different but valid permutation must not be
            # accepted (only the canonical order scores).
            lbl = other.split(",")
            if len(lbl) >= 2:
                bad = lbl[1] + "," + lbl[0] + "," + ",".join(lbl[2:])
                assert t.score_answer(bad, ex) < 1.0 or bad == other


def test_analyze_basic_cycle():
    # T1 W x, T2 W x, T1 W x -> write-write edges T1->T2 and T2->T1
    ops = [(1, "W", "x1"), (2, "W", "x1"), (1, "W", "x1")]
    serializable, order = analyze(ops)
    assert not serializable


def test_analyze_linear():
    # T1 W x, T1 R y, T2 R x, T3 W y -> edges 1->2, 1->3, no back edge
    ops = [(1, "W", "x1"), (1, "R", "x1"), (2, "R", "x1"), (3, "W", "x1")]
    serializable, order = analyze(ops)
    assert serializable
    assert order == "T1,T2,T3"


def test_difficulty_changes():
    t = TransactionSerializability()
    r = TransactionSerializability()
    t.config.set_level(0)
    r.config.set_level(5)
    assert t.config.n_ops < r.config.n_ops
