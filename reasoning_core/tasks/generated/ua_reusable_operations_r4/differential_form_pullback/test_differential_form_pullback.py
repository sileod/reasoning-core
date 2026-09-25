import itertools
import random

from reasoning_core.tasks.generated.ua_reusable_operations_r4.differential_form_pullback.differential_form_pullback import (
    DifferentialFormPullback,
    DifferentialFormPullbackConfig,
    _parse_answer,
    _canonical_equal,
)


def _task(level=0):
    t = DifferentialFormPullback()
    t.config.set_level(level)
    return t


def test_gold_scores_one_at_levels():
    for lvl in (0, 2, 5, 6):
        t = _task(lvl)
        for _ in range(20):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_junk_and_empty_score_zero():
    t = _task(0)
    for _ in range(20):
        ex = t.generate_example()
        assert t.score_answer("", ex) == 0.0
        assert t.score_answer("garbage", ex) == 0.0
        assert t.score_answer("import os", ex) == 0.0


def test_wrong_permutation_scores_zero():
    t = _task(5)
    for _ in range(10):
        ex = t.generate_example()
        if "^" not in ex.answer:
            continue
        swapped = ex.answer.replace("^", "*")
        if swapped != ex.answer:
            assert t.score_answer(swapped, ex) == 0.0


def test_parser_roundtrip_on_gold():
    t = _task(0)
    for lvl in (0, 2, 5):
        t.config.set_level(lvl)
        for _ in range(20):
            ex = t.generate_example()
            rep = _parse_answer(ex.answer, ex.metadata["target_names"])
            assert _canonical_equal(rep, _parse_answer(ex.answer, ex.metadata["target_names"]))


def test_metadata_json_serializable():
    import json
    t = _task(3)
    for _ in range(5):
        ex = t.generate_example()
        json.dumps(dict(ex.metadata))


def test_difficulty_changes_config():
    t = DifferentialFormPullback()
    c0 = t.config.to_dict()
    t.config.set_level(1)
    c1 = t.config.to_dict()
    assert c1 != c0


def test_levels_produce_examples():
    for lvl in range(7):
        t = _task(lvl)
        ex = t.generate_example()
        assert ex.answer


def test_no_constant_answer():
    random.seed(99)
    t = _task(0)
    answers = {t.generate_example().answer for _ in range(30)}
    assert len(answers) >= 10


def test_config_class_used():
    assert DifferentialFormPullback.config_cls is DifferentialFormPullbackConfig
