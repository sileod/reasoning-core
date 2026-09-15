from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_dependence_relevance_r1.simpson_reversal_detection.simpson_reversal_detection import (
    SimpsonReversalDetection,
)


def test_generate_and_roundtrip():
    task = SimpsonReversalDetection()
    for _ in range(50):
        ex = task.generate_example()
        assert isinstance(ex, Entry)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_difficulty_changes_config():
    task = SimpsonReversalDetection()
    c0 = SimpsonReversalDetection()
    c6 = SimpsonReversalDetection()
    c0.config.set_level(0)
    c6.config.set_level(6)
    assert c6.config.strat_count >= c0.config.strat_count
    assert c6.config.max_n >= c0.config.max_n


def test_scorer_garbage():
    task = SimpsonReversalDetection()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("maybe", ex) == 0.0
    gold = ex.answer
    other = "no" if gold == "yes" else "yes"
    assert task.score_answer(other, ex) == 0.0


def test_labels_balanced():
    task = SimpsonReversalDetection()
    counts = {"no": 0, "reversal": 0}
    for _ in range(400):
        ex = task.generate_example()
        if ex.answer == "no":
            counts["no"] += 1
        else:
            counts["reversal"] += 1
    total = sum(counts.values())
    assert counts["no"] >= 0.25 * total
    assert counts["reversal"] >= 0.25 * total
