import random

import pytest

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.polarity_item_licensing.polarity_item_licensing import (
    PolarityItemLicensing,
    LICENSORS,
    _main_clause,
)


@pytest.fixture(params=[0, 1, 3, 6])
def task(request):
    t = PolarityItemLicensing()
    t.config.set_level(request.param)
    return t


def test_generate_and_score(task):
    for _ in range(40):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("garbage", e) == 0.0


def test_answer_in_vocabulary():
    t = PolarityItemLicensing()
    for level in [0, 1, 2, 3, 4, 5, 6]:
        t.config.set_level(level)
        seen = set()
        for _ in range(60):
            e = t.generate_example()
            assert e.answer in LICENSORS
            seen.add(e.answer)
        # structure varies and more than one distinct answer per level
        assert len(seen) > 1


def test_balance_not_constant():
    t = PolarityItemLicensing()
    counts = {}
    for _ in range(400):
        e = t.generate_example()
        counts[e.answer] = counts.get(e.answer, 0) + 1
    # every label occurs; unlicensed present
    for lab in LICENSORS:
        assert counts.get(lab, 0) > 0


def test_prompt_has_vocabulary_and_question():
    t = PolarityItemLicensing()
    t.config.set_level(0)
    e = t.generate_example()
    p = t.render_prompt(e.metadata)
    assert "negation" in p
    assert "unlicensed" in p
    assert "Which licensor" in p


def test_metadata_json_serializable():
    import json

    t = PolarityItemLicensing()
    t.config.set_level(6)
    for _ in range(10):
        e = t.generate_example()
        json.dumps(dict(e.metadata))
