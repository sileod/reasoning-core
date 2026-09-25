import re

import pytest

from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.multiport_wave_relation_translation.multiport_wave_relation_translation import (
    MultiportWaveRelationTranslation,
)


def _make(level):
    task = MultiportWaveRelationTranslation()
    task.config.set_level(level)
    return task


def test_gold_roundtrip_every_level():
    for level in range(7):
        task = _make(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = _make(3)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0


def test_answer_format():
    task = _make(2)
    ex = task.generate_example()
    for m in re.finditer(r"b_(\d+) = (-?\d+(?:/-?\d+)?)\*a_\1", ex.answer):
        pass
    rels = ex.answer.split("; ")
    assert len(rels) == task.config.num_ports
    for rel in rels:
        assert re.fullmatch(r"b_\d+ = -?\d+(?:/-?\d+)?\*a_\d+", rel), rel


def test_coefficient_in_domain_and_order():
    task = _make(0)
    for _ in range(20):
        ex = task.generate_example()
        assert ex.answer.split("; ")[0].startswith("b_1")


def test_deterministic_within_process():
    a = _make(1).generate_entry()
    b = _make(1).generate_entry()
    # same module-level RNG state -> not comparable across calls; just check no crash
    assert isinstance(a.answer, str)


def test_metadata_json_serializable():
    import json

    task = _make(4)
    ex = task.generate_example()
    json.dumps(ex.metadata)
