import pytest

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.convex_hull_ordering.convex_hull_ordering import (
    ConvexHullOrdering,
    _parse_eq,
    design_choice,
)


def test_design_choice_present():
    assert isinstance(design_choice, str) and len(design_choice) > 10


def test_generate_and_score():
    task = ConvexHullOrdering()
    for level in [0, 3, 6]:
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_fails():
    task = ConvexHullOrdering()
    task.config.set_level(0)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("not,a;list", ex) == 0.0
    assert task.score_answer("999,999;1,1", ex) == 0.0


def test_rotation_invariant_answer_scores():
    task = ConvexHullOrdering()
    task.config.set_level(0)
    for _ in range(20):
        ex = task.generate_example()
        gold = _parse_eq(ex.answer)
        if len(gold) < 3:
            continue
        for start in range(len(gold)):
            rotated = gold[start:] + gold[:start]
            s = ";".join(f"{p[0]},{p[1]}" for p in rotated)
            assert task.score_answer(s, ex) == 1.0


def test_reverse_order_is_valid():
    task = ConvexHullOrdering()
    task.config.set_level(0)
    for _ in range(20):
        ex = task.generate_example()
        gold = _parse_eq(ex.answer)
        if len(gold) < 3:
            continue
        rev = list(reversed(gold))
        s = ";".join(f"{p[0]},{p[1]}" for p in rev)
        assert task.score_answer(s, ex) == 1.0


def test_wrong_points_fail():
    task = ConvexHullOrdering()
    task.config.set_level(0)
    for _ in range(20):
        ex = task.generate_example()
        gold = _parse_eq(ex.answer)
        if len(gold) < 3:
            continue
        missing = gold[1:]
        s = ";".join(f"{p[0]},{p[1]}" for p in missing)
        assert task.score_answer(s, ex) == 0.0
