import json
import random

from reasoning_core.tasks.generated.ua_dynamic_structures_r4.anyon_fusion_reassociation.anyon_fusion_reassociation import (
    AnyonFusionConfig,
    AnyonFusionReassociation,
    _score_amplitude,
)


def test_summary_literal():
    t = AnyonFusionReassociation()
    assert isinstance(t.summary, str) and t.summary.strip()
    assert "F" in t.summary and "R" in t.summary and "fusion" in t.summary


def test_generate_and_score():
    t = AnyonFusionReassociation()
    x = t.generate_example()
    assert t.score_answer(x.answer, x) == 1
    assert t.score_answer("", x) < 1
    assert t.score_answer("zzz999", x) < 1
    assert int(x.answer) == int(x.metadata["amplitude"])


def test_answer_is_integer_in_metadata():
    t = AnyonFusionReassociation()
    for _ in range(20):
        x = t.generate_example()
        assert int(x.answer) == int(x.metadata["amplitude"])
        assert isinstance(x.metadata["amplitude"], int)


def test_difficulty_changes_config():
    t = AnyonFusionReassociation()
    t.config.set_level(0)
    n0 = t.config.n
    t.config.set_level(6)
    n6 = t.config.n
    assert n6 > n0


def test_json_roundtrip():
    t = AnyonFusionReassociation()
    x = t.generate_example()
    rt = json.loads(json.dumps(dict(x.metadata)))
    assert rt["amplitude"] == x.metadata["amplitude"]


def test_not_constant_across_answers():
    t = AnyonFusionReassociation()
    answers = {t.generate_example().answer for _ in range(40)}
    assert len(answers) > 1


def test_all_levels_generate():
    t = AnyonFusionReassociation()
    for lvl in (0, 1, 2, 3, 4, 5, 6):
        x = t.generate_example(level=lvl)
        assert t.score_answer(x.answer, x) == 1


def test_score_helper():
    assert _score_amplitude(" 2 ", "2") == 1.0
    assert _score_amplitude("+3", "3") == 1.0
    assert _score_amplitude("2", "3") == 0.0
    assert _score_amplitude("abc", "2") == 0.0
