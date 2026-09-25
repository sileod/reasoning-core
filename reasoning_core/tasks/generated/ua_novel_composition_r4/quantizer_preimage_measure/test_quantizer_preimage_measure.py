import random
from fractions import Fraction

import pytest

from reasoning_core.template import Config
from reasoning_core.tasks.generated.ua_novel_composition_r4.quantizer_preimage_measure.quantizer_preimage_measure import (
    QuantizerPreimageMeasure,
    QuantizerPreimageMeasureConfig,
    _measure_code,
    _fmt_fraction,
    _parse_fraction,
)


def test_summary_and_design_choice():
    assert isinstance(QuantizerPreimageMeasure.summary, str)
    assert QuantizerPreimageMeasure.summary.strip()
    assert "Invert cascades" in QuantizerPreimageMeasure.summary
    assert isinstance(QuantizerPreimageMeasure.design_choice, str)


def test_generate_and_score_roundtrip():
    random.seed(1234)
    task = QuantizerPreimageMeasure()
    ex = task.generate_example()
    assert ex.prompt
    assert ex.answer
    assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_is_reduced_fraction_in_unit_interval():
    random.seed(7)
    task = QuantizerPreimageMeasure()
    for _ in range(30):
        ex = task.generate_example()
        fr = _parse_fraction(ex.answer)
        assert fr == Fraction(fr.numerator, fr.denominator)  # valid
        assert ex.metadata["answer_num"] == fr.numerator
        assert ex.metadata["answer_den"] == fr.denominator
        assert 0 <= fr <= 1
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_rejects_junk_and_wrong_answers():
    random.seed(99)
    task = QuantizerPreimageMeasure()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("garbage!!", ex) < 1.0
    gold = _parse_fraction(ex.answer)
    wrong = gold + 1 if gold + 1 <= 1 else gold / 2
    assert task.score_answer(_fmt_fraction(wrong), ex) < 1.0


def test_semantic_scoring_reduces_equivalent_fractions():
    random.seed(5)
    task = QuantizerPreimageMeasure()
    ex = task.generate_example()
    gold = _parse_fraction(ex.answer)
    scaled = Fraction(gold.numerator * 3, gold.denominator * 3)
    assert task.score_answer(_fmt_fraction(scaled), ex) == 1.0


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_generates_at_all_levels(level):
    random.seed(level * 100)
    cfg = QuantizerPreimageMeasureConfig()
    cfg.set_level(level)
    task = QuantizerPreimageMeasure(cfg)
    ex = task.generate_example()
    assert ex.metadata["_level"] == level
    assert task.score_answer(ex.answer, ex) == 1.0


def test_difficulty_changes_config():
    cfg = QuantizerPreimageMeasureConfig()
    c0 = (cfg.bins, cfg.teeth, cfg.base_span)
    cfg.set_level(4)
    c4 = (cfg.bins, cfg.teeth, cfg.base_span)
    assert c0 != c4
    assert cfg.bins > c0[0]
    assert cfg.teeth > c0[1]


def test_metadata_json_serializable():
    import json
    random.seed(42)
    task = QuantizerPreimageMeasure()
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))
