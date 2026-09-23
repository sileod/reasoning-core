import random

parent = __file__.rsplit("/", 1)[0] + "/"
import sys

sys.path.insert(0, parent)
from unary_resource_edge_finding import (
    UnaryResourceEdgeFinding,
    _feasible,
    _target_bounds,
)


def _build(n, horizon, max_dur, seed):
    return UnaryResourceEdgeFinding()


def test_gold_scores():
    t = UnaryResourceEdgeFinding()
    for _ in range(30):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_bad_scores():
    t = UnaryResourceEdgeFinding()
    for _ in range(30):
        e = t.generate_example()
        assert t.score_answer("zzz", e) == 0.0
        assert t.score_answer("", e) == 0.0
        assert t.score_answer(str(int(e.answer) + 1), e) == 0.0


def test_domain():
    t = UnaryResourceEdgeFinding()
    for _ in range(30):
        e = t.generate_example()
        a = int(e.answer)
        win = e.metadata["window"]
        assert win[0] <= a <= win[1]
        assert 0 <= a
        jobs = e.metadata["jobs"]
        target = e.metadata["target"]
        tr, td = win
        assert tr <= td


def test_balance_levels():
    for level in (0, 3, 6):
        t = UnaryResourceEdgeFinding()
        t.config.set_level(level)
        seen = {e.answer for _ in range(40) for e in [t.generate_example()]}
        assert len(seen) > 3, f"too few distinct answers at level {level}: {seen}"


def test_feasibility_helper():
    assert _feasible([(0, 5, 3), (3, 9, 2)])
    # infeasible: two jobs must both run in overlapping single slot
    assert not _feasible([(0, 4, 3), (1, 4, 4)])
