import random
from fractions import Fraction

from reasoning_core.tasks.generated.ua_representation_specific_r4.partition_rim_strip_cancellation.partition_rim_strip_cancellation import (
    PartitionRimStripCancellation,
    format_fraction,
    signed_total,
)


def test_validate():
    t = PartitionRimStripCancellation()
    t.validate()


def test_roundtrip_all_levels():
    t = PartitionRimStripCancellation()
    for lvl in range(7):
        t.config.set_level(lvl)
        seen = set()
        for _ in range(8):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0
            assert t.score_answer("", ex) < 1.0
            assert t.score_answer("not a fraction", ex) < 1.0
            assert t.score_answer("999999999/1", ex) < 1.0
            seen.add(ex.answer)
        assert len(seen) > 1


def test_fraction_is_reduced():
    t = PartitionRimStripCancellation()
    for lvl in range(7):
        t.config.set_level(lvl)
        for _ in range(20):
            ex = t.generate_example()
            num, _, den = ex.answer.partition("/")
            n, d = int(num), int(den)
            assert d > 0
            assert Fraction(n, d) == Fraction(n, d).limit_denominator()
            assert n != 0


def test_known_staircase():
    part = [3, 2, 1]
    assert signed_total(part, [1]) == Fraction(3, 1)
    assert format_fraction(Fraction(3, 1)) == "3/1"
    assert format_fraction(Fraction(-5, 2)) == "-5/2"
    assert format_fraction(Fraction(0, 1)) == "0/1"


def test_score_rejects_wrong_fraction():
    t = PartitionRimStripCancellation()
    t.config.set_level(0)
    ex = t.generate_example()
    gold = Fraction(ex.answer)
    assert Fraction(ex.answer) == gold
    wrong = format_fraction(Fraction(-gold.numerator, gold.denominator))
    assert t.score_answer(wrong, ex) == 0.0
