import math

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.selective_evidence_conditioning.selective_evidence_conditioning import (
    SelectiveEvidenceConditioning,
    _format_ratio,
    _parse_ratio,
)


def test_generate_and_score():
    task = SelectiveEvidenceConditioning()
    x = task.generate_example()
    assert x.answer is not None
    assert task.score_answer(x.answer, x) == 1.0


def test_difficulty_changes_config():
    task = SelectiveEvidenceConditioning()
    low = task.generate_example()
    config = task.config_cls()
    config.set_level(1)
    assert config.k >= low.metadata["k"] or config.M >= low.metadata["M"]


def test_junk_not_scored():
    task = SelectiveEvidenceConditioning()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("banana", x) == 0.0


def test_defining_property_holds():
    from fractions import Fraction

    task = SelectiveEvidenceConditioning()
    for _ in range(20):
        x = task.generate_example()
        m = x.metadata
        wA, wB, M, k, w = m["weightsA"], m["weightsB"], m["support"], m["k"], m["winner"]
        rep = m["rep"]
        WA, WB = sum(wA), sum(wB)
        SA, SB = sum(wA[: w - 1]), sum(wB[: w - 1])
        numA = wA[w - 1] * (SA ** (k - 1))
        numB = wB[w - 1] * (SB ** (k - 1))
        denA, denB = WA ** k, WB ** k
        if m["followup"]:
            numA *= wA[rep - 1]
            numB *= wB[rep - 1]
            denA *= WA
            denB *= WB
        lr = Fraction(numA * denB, numB * denA)
        assert (m["gold_num"], m["gold_den"]) == (lr.numerator, lr.denominator)
        assert lr > 0


def test_format_roundtrip():
    assert _format_ratio(3, 1) == "3"
    assert _parse_ratio("3") == (3, 1)
    assert _parse_ratio("6/4") == (3, 2)


def test_positive_domain():
    task = SelectiveEvidenceConditioning()
    for _ in range(30):
        x = task.generate_example()
        assert x.metadata["gold_num"] > 0
        assert x.metadata["gold_den"] > 0
