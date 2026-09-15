import pytest
from fractions import Fraction

import reasoning_core.tasks.generated.k3_uncertainty_r1.censored_survival_estimate.censored_survival_estimate as mod


@pytest.fixture
def task_cls():
    return mod.CensoredSurvivalEstimate


def test_generate_and_score(task_cls):
    t = task_cls()
    for level in (0, 2, 5):
        t.config.set_level(level)
        for _ in range(25):
            x = t.generate_example()
            assert t.score_answer(x.answer, x) == 1.0
            assert t.score_answer("", x) < 1.0
            assert t.score_answer("junk", x) < 1.0
            assert t.score_answer(None, x) < 1.0


def test_answer_matches_fraction(task_cls):
    t = task_cls()
    t.config.set_level(3)
    for _ in range(25):
        x = t.generate_example()
        m = x.metadata
        f = Fraction(m["numerator"], m["denominator"])
        assert "%d/%d" % (f.numerator, f.denominator) == x.answer
        assert 0 <= f <= 1


def test_domain_and_at_risk(task_cls):
    t = task_cls()
    for level in (0, 3, 6):
        t.config.set_level(level)
        for _ in range(30):
            x = t.generate_example()
            m = x.metadata
            events = sorted(m["event_days"])
            withdrawals = sorted(m["withdraw_days"])
            assert events and withdrawals
            assert len(events) + len(withdrawals) == m["num_subjects"]
            assert len(set(events)) == len(events)
            assert set(events).isdisjoint(withdrawals)
            assert m["query_day"] >= events[0]


def test_difficulty_changes(task_cls):
    t = task_cls()
    t.config.set_level(0)
    base = (t.config.num_subjects, t.config.horizon)
    t.config.set_level(6)
    assert (t.config.num_subjects, t.config.horizon) > base


def test_summary_and_design_choice(task_cls):
    assert task_cls.summary
    assert "reduced fraction" in task_cls.design_choice


def test_meta_present():
    assert mod.TASK_META["hypothesis"] == "P007"
    assert mod.TASK_META["parent_source_id"] is None
