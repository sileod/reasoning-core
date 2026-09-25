import random

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.loss_coverage_equivalence.loss_coverage_equivalence import (
    LossCoverageEquivalence,
)


def _make_task(level):
    task = LossCoverageEquivalence()
    task.config.set_level(level)
    return task


def test_gold_scores_one():
    random.seed(2302342651)
    task = _make_task(0)
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = _make_task(0)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("yes", ex) == 0.0
    assert task.score_answer("identical", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0


def test_answers_are_labeled():
    task = _make_task(5)
    seen = set()
    for _ in range(40):
        ex = task.generate_example()
        seen.add(ex.answer)
    assert seen <= {"same", "different"}


def test_both_labels_occur_at_every_level():
    for level in (0, 2, 5):
        task = _make_task(level)
        seen = set()
        for _ in range(30):
            seen.add(task.generate_example().answer)
        assert seen == {"same", "different"}, f"level {level} not balanced: {seen}"


def test_different_answers_are_genuinely_different():
    task = _make_task(3)
    for _ in range(30):
        ex = task.generate_example()
        if ex.answer != "different":
            continue
        pa = ex.metadata["policy_a"]
        pb = ex.metadata["policy_b"]
        assert pa != pb, "different-labeled policies should differ in text"


def test_deterministic_under_seed():
    random.seed(99)
    t1 = _make_task(2)
    a1 = t1.generate_example().answer
    random.seed(99)
    t2 = _make_task(2)
    a2 = t2.generate_example().answer
    assert a1 == a2
