import random

from reasoning_core.tasks.generated.ua_representation_specific_r4.multivalued_dependency_closure.multivalued_dependency_closure import (
    MultivaluedDependencyClosure,
)


def test_generate_and_score():
    task = MultivaluedDependencyClosure()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert ex.metadata["attrs"] == [0, 1, 2]
            assert ex.answer in ("yes", "no")
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = MultivaluedDependencyClosure()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("bogus", ex) < 1.0
    opp = "no" if ex.answer == "yes" else "yes"
    assert task.score_answer(opp, ex) < 1.0


def test_difficulty_changes():
    task = MultivaluedDependencyClosure()
    task.config.set_level(0)
    l0 = (task.config.nbase, task.config.nfds)
    task.config.set_level(6)
    l6 = (task.config.nbase, task.config.nfds)
    assert l0 != l6


def test_balanced_labels():
    task = MultivaluedDependencyClosure()
    counts = {"yes": 0, "no": 0}
    for _ in range(200):
        ex = task.generate_example()
        counts[ex.answer] += 1
    assert counts["yes"] > 0 and counts["no"] > 0
