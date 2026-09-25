import itertools
import random
from fractions import Fraction

from reasoning_core.tasks.generated.ua_latent_representation_r4.experiment_garbling_order.experiment_garbling_order import (
    ExperimentGarblingOrder,
    _feasible_garbling,
    _matmul,
    _unit_garbling,
)


def _run(task, n=200):
    labels = []
    for _ in range(n):
        ex = task.generate_example()
        assert ex.answer in ("yes", "no")
        labels.append(ex.answer)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("yes" if ex.answer == "no" else "no", ex) == 0.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("maybe", ex) == 0.0
    return labels


def test_balanced_labels_per_level():
    for level in (0, 3, 6):
        task = ExperimentGarblingOrder()
        task.config.set_level(level)
        labels = _run(task, 200)
        yes = labels.count("yes")
        assert 0.1 <= yes / len(labels) <= 0.9, (level, yes, len(labels))


def test_exact_feasibility_roundtrip():
    task = ExperimentGarblingOrder()
    for _ in range(300):
        ex = task.generate_example()
        A = [[Fraction(c, 3) for c in row] for row in ex.metadata["A"]]
        B = [[Fraction(c, 3) for c in row] for row in ex.metadata["B"]]
        label = ex.answer == "yes"
        assert _feasible_garbling(A, B) == label


def test_constructed_yes_is_real():
    task = ExperimentGarblingOrder()
    got_constructed = 0
    for _ in range(300):
        ex = task.generate_entry()
        A = [[Fraction(c, 3) for c in row] for row in ex.metadata["A"]]
        B = [[Fraction(c, 3) for c in row] for row in ex.metadata["B"]]
        assert _feasible_garbling(A, B) == (ex.answer == "yes")
        if ex.answer == "yes":
            got_constructed += 1
    assert got_constructed > 0


def test_render_deterministic_and_limit():
    task = ExperimentGarblingOrder()
    task.config.set_level(6)
    for _ in range(5):
        ex = task.generate_example()
        p1 = task.render_prompt(ex.metadata)
        p2 = task.render_prompt(ex.metadata)
        assert p1 == p2
        assert len(p1.split()) < 300
