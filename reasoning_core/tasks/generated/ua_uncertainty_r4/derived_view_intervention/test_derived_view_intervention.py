import random

from reasoning_core.tasks.generated.ua_uncertainty_r4.derived_view_intervention.derived_view_intervention import (
    DerivedViewIntervention,
    _feasible,
)


def _fresh(level=0):
    random.seed(123 + level)
    return DerivedViewIntervention()


def test_gold_scores_one():
    task = _fresh()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_balanced():
    task = _fresh()
    counts = {"Yes": 0, "No": 0}
    for _ in range(120):
        ex = task.generate_example()
        counts[ex.answer] += 1
    assert counts["Yes"] > 0 and counts["No"] > 0
    assert min(counts.values()) / max(counts.values()) > 0.25


def test_wrong_and_junk():
    task = _fresh()
    ex = task.generate_example()
    assert task.score_answer("No" if ex.answer == "Yes" else "Yes", ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("17", ex) == 0.0


def test_feasibility_is_ground_truth():
    task = _fresh()
    for _ in range(60):
        ex = task.generate_example()
        m = ex.metadata
        left = list(range(len(m["left"])))
        right = list(range(len(m["right"])))
        edges = set((l, r) for (l, r) in m["edges"])
        a = int(m["a"][1:])
        b = int(m["b"][1:])
        feas = _feasible(a, b, left, right, edges)
        assert (feas == "yes") == m["answer_yes"]
        assert (feas == "yes") == (ex.answer == "Yes")


def test_distinct_levels():
    task = _fresh()
    lens = set()
    a_vals = set()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        lens.add(list(map(len, (ex.metadata["left"], ex.metadata["right"])))[0])
        a_vals.add(ex.metadata["a"])
    assert min(lens) < max(lens)


def test_validate_contract():
    task = _fresh()
    task.validate(n_samples=6)
