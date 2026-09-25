import random

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.phase_change_equilibration import (
    phase_change_equilibration as m,
)


def test_generate_example():
    random.seed(1)
    t = m.PhaseChangeEquilibration()
    x = t.generate_example()
    assert isinstance(x.answer, str)
    assert m._score(x.answer, x.metadata) == 1.0


def test_gold_scores_one_many():
    random.seed(123)
    t = m.PhaseChangeEquilibration()
    for _ in range(200):
        x = t.generate_example()
        assert m._score(x.answer, x.metadata) == 1.0


def test_wrong_answers_fail():
    random.seed(7)
    t = m.PhaseChangeEquilibration()
    for _ in range(100):
        x = t.generate_example()
        assert m._score("999 9/9", x.metadata) < 1.0
        assert m._score("0 0/1", x.metadata) < 1.0
        assert m._score("", x.metadata) == 0.0
        assert m._score("garbage", x.metadata) == 0.0


def test_balance_and_regimes():
    random.seed(42)
    t = m.PhaseChangeEquilibration()
    regimes = {"liq": 0, "mix": 0, "sol": 0}
    for _ in range(600):
        x = t.generate_example()
        # generate_entry internally verifies the enthalpy balance on the
        # unrounded temperature, so a gold that scores 1.0 is balance-consistent
        assert m._score(x.answer, x.metadata) == 1.0
        f = float(x.metadata["frac"].split("/")[0]) / float(x.metadata["frac"].split("/")[1])
        if f < 1e-9:
            regimes["liq"] += 1
        elif f > 1 - 1e-9:
            regimes["sol"] += 1
        else:
            regimes["mix"] += 1
    assert all(v > 0 for v in regimes.values()), regimes


def test_validate():
    t = m.PhaseChangeEquilibration()
    t.validate()


def test_difficulty_changes_config():
    t = m.PhaseChangeEquilibration()
    base = t.config.mass_range[1]
    t.config.set_level(6)
    assert t.config.mass_range[1] > base


def test_deterministic():
    random.seed(99)
    t = m.PhaseChangeEquilibration()
    a = [t.generate_entry().answer for _ in range(50)]
    random.seed(99)
    t2 = m.PhaseChangeEquilibration()
    b = [t2.generate_entry().answer for _ in range(50)]
    assert a == b
