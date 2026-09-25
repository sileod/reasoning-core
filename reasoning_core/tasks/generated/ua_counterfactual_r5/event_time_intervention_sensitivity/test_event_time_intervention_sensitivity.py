import random
from fractions import Fraction

from reasoning_core.template import Entry

from .event_time_intervention_sensitivity import (
    EventTimeInterventionSensitivity,
    _parse_fraction,
    _final_time,
    _finite_sensitivity,
)


def test_smoke_and_scoring():
    task = EventTimeInterventionSensitivity()
    for _ in range(20):
        ex = task.generate_example()
        assert isinstance(ex, Entry)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("banana", ex) == 0.0


def test_chain_difficulty_changes():
    task = EventTimeInterventionSensitivity()
    task.config.set_level(0)
    l0 = task.config.max_legs
    task.config.set_level(6)
    l6 = task.config.max_legs
    assert l6 > l0


def test_answer_rock_against_recomputation():
    task = EventTimeInterventionSensitivity()
    task.config.set_level(6)
    for _ in range(20):
        ex = task.generate_example()
        md = ex.metadata
        x0 = md["x0"]
        legs = [(a, s, l) for a, s, l in md["legs"]]
        resets = [(al, be) for al, be in md["resets"]]
        expected = str(Fraction(_final_time(x0, legs, resets)) if False else _analytic(x0, legs, resets))
        fin = _finite_sensitivity(x0, legs, resets)
        assert float(abs(Fraction(expected) - fin)) < 1e-6


def _analytic(x0, legs, resets):
    x = Fraction(x0)
    dxdx0 = Fraction(1)
    dTdx0 = Fraction(0)
    for (a, s, l), (al, be) in zip(legs, resets):
        dtau_dx = Fraction(-1, a - s)
        dTdx0 += dtau_dx * dxdx0
        dxat_dx = 1 + Fraction(a) * dtau_dx
        dxdx0 = Fraction(al) * dxat_dx * dxdx0
    return dTdx0


def test_score_rejects_other_instance():
    task = EventTimeInterventionSensitivity()
    a = task.generate_example()
    b = task.generate_example()
    if a.answer != b.answer:
        assert task.score_answer(b.answer, a) == 0.0


def test_all_levels_produce():
    task = EventTimeInterventionSensitivity()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        answers = set()
        for _ in range(10):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            answers.add(ex.answer)
        assert len(answers) > 1
