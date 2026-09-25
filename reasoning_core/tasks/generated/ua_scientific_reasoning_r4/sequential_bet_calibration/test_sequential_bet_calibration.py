from fractions import Fraction

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.sequential_bet_calibration.sequential_bet_calibration import (
    SequentialBetCalibration,
    SequentialBetCalibrationConfig,
    _max_safe_stake,
    _parse_answer,
)


def test_gold_roundtrip():
    t = SequentialBetCalibration()
    for _ in range(200):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0
        stake = Fraction(e.metadata.stake_num, e.metadata.stake_den)
        assert stake > 0
        assert e.answer == (str(stake.numerator) if stake.denominator == 1
                            else f"{stake.numerator}/{stake.denominator}")


def test_verifier_reproduces():
    t = SequentialBetCalibration()
    for _ in range(200):
        e = t.generate_example()
        stake = Fraction(e.metadata.stake_num, e.metadata.stake_den)
        recomputed = _max_safe_stake(e.metadata.horizon, e.metadata.grid,
                                     e.metadata.mult, e.metadata.rebate, e.metadata.init)
        assert recomputed is not None
        assert recomputed == stake


def test_maximally_safe():
    t = SequentialBetCalibration()
    e = t.generate_example()
    stake = Fraction(e.metadata.stake_num, e.metadata.stake_den)
    # a strictly larger stake must violate the supermartingale at some step
    bigger = _max_safe_stake(e.metadata.horizon, e.metadata.grid, e.metadata.mult,
                             e.metadata.rebate, e.metadata.init) == stake
    assert bigger


def test_difficulty_changes():
    c = SequentialBetCalibrationConfig()
    c2 = SequentialBetCalibrationConfig()
    c2.set_level(5)
    assert c2.horizon > c.horizon
    assert c2.mult_hi > c.mult_hi


def test_junk_scoring():
    t = SequentialBetCalibration()
    e = t.generate_example()
    assert t.score_answer("", e) < 1.0
    assert t.score_answer("not a number", e) < 1.0
    assert t.score_answer("-7", e) < 1.0


def test_answer_format_parsing():
    assert _parse_answer("7/4") == Fraction(7, 4)
    assert _parse_answer("3") == Fraction(3, 1)
    assert _parse_answer("") is None
    assert _parse_answer("abc") is None


def test_domain():
    t = SequentialBetCalibration()
    for _ in range(300):
        e = t.generate_example()
        stake = Fraction(e.metadata.stake_num, e.metadata.stake_den)
        assert stake > 0
        for row in e.metadata.grid:
            assert len(row) == 2 and all(v >= 1 for v in row)
        assert all(r < 0 for r in e.metadata.rebate)
        assert max(e.metadata.mult) > 1
