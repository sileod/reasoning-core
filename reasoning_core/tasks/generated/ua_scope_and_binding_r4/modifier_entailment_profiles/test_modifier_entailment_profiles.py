import random
from pathlib import Path

import pytest

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.modifier_entailment_profiles.modifier_entailment_profiles import (
    ModifierEntailmentProfiles,
)


@pytest.fixture
def task():
    return ModifierEntailmentProfiles()


def test_gold_scores_one(task):
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_empty_and_junk_score_zero(task):
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("garbage", ex) < 1.0


def test_summary_present():
    assert "entailed" in ModifierEntailmentProfiles.summary
    assert "modifier" in ModifierEntailmentProfiles.summary


def test_design_choice_present():
    assert "scope" in ModifierEntailmentProfiles.design_choice


def test_difficulty_changes_config(task):
    base = ModifierEntailmentProfiles()
    base.config.set_level(0)
    v0 = base.config.modifiers
    hi = ModifierEntailmentProfiles()
    hi.config.set_level(6)
    v6 = hi.config.modifiers
    assert v6 >= v0


def test_generation_all_levels():
    for level in range(7):
        t = ModifierEntailmentProfiles()
        t.config.set_level(level)
        ex = t.generate_example()
        assert isinstance(ex.answer, str)
        assert t.score_answer(ex.answer, ex) == 1.0


def test_metadata_json_serializable(task):
    import json

    ex = task.generate_example()
    json.dumps(ex.metadata)


def test_not_constant_answer():
    answers = set()
    for _ in range(120):
        ex = ModifierEntailmentProfiles().generate_example()
        answers.add(ex.answer)
    assert len(answers) >= 4


def test_reproducible_seeded():
    import importlib

    mod = importlib.import_module(
        "reasoning_core.tasks.generated.ua_scope_and_binding_r4.modifier_entailment_profiles.modifier_entailment_profiles"
    )
    random.seed(1234)
    a = [mod.ModifierEntailmentProfiles().generate_example().answer for _ in range(10)]
    random.seed(1234)
    b = [mod.ModifierEntailmentProfiles().generate_example().answer for _ in range(10)]
    assert a == b


def test_answer_never_empty():
    for _ in range(200):
        t = ModifierEntailmentProfiles()
        ex = t.generate_example()
        ans = {p for p in ex.answer.split(",") if p}
        assert bool(ans), "answer should never be empty since outermost is intersective"


def test_lexicon_order_respected():
    order = ["animate", "concrete", "material", "liquid", "container", "edible", "sharp"]
    for _ in range(50):
        ex = ModifierEntailmentProfiles().generate_example()
        seq = ex.answer.split(",")
        idxs = [order.index(p) for p in seq]
        assert idxs == sorted(idxs)
