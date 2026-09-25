import random

from reasoning_core.template import Entry, Task

from reasoning_core.tasks.generated.ua_counterfactual_r4.qualitative_limit_path_dependence.qualitative_limit_path_dependence import (
    QualitativeLimitPathDependence,
)


def test_validates():
    t = QualitativeLimitPathDependence()
    t.validate()


def test_roundtrip_and_answer_format():
    random.seed(1234)
    t = QualitativeLimitPathDependence()
    for _ in range(200):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_garbage_scores_zero():
    random.seed(99)
    t = QualitativeLimitPathDependence()
    for _ in range(100):
        e = t.generate_example()
        for junk in ("", "abc", "DIVERGES " + "x", "0/0", "1/0"):
            assert t.score_answer(junk, e) < 1.0, (junk, e.answer)


def test_gameability_diverges_not_constant():
    random.seed(7)
    t = QualitativeLimitPathDependence()
    modes = []
    for _ in range(120):
        e = t.generate_example()
        modes.append(e.answer == "DIVERGES")
    conv = sum(1 for m in modes if not m)
    dv = sum(modes)
    assert abs(conv - dv) <= 60, (conv, dv)


def test_difficulty_changes_config():
    t = QualitativeLimitPathDependence()
    t.config.set_level(0)
    l0 = t.config.maxc
    t.config.set_level(6)
    assert t.config.maxc > l0


def test_levels_generate():
    t = QualitativeLimitPathDependence()
    for lvl in (0, 1, 2, 3, 4, 5, 6):
        t.config.set_level(lvl)
        for _ in range(20):
            e = t.generate_example()
            assert t.score_answer(e.answer, e) == 1.0


def test_metadata_json_serializable():
    import json

    random.seed(5)
    t = QualitativeLimitPathDependence()
    for _ in range(20):
        e = t.generate_example()
        json.dumps(e.metadata)
