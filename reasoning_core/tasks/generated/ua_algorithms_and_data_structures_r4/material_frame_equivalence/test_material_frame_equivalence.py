import random

import pytest

from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.material_frame_equivalence.material_frame_equivalence import (
    MaterialFrameEquivalence,
)


def _task(level=0):
    t = MaterialFrameEquivalence()
    t.config.set_level(level)
    return t


def test_summary_and_design_choice_present():
    t = MaterialFrameEquivalence()
    assert isinstance(t.summary, str) and len(t.summary) > 40
    assert "material points" in t.summary and "velocity" in t.summary and "yes/no" in t.summary
    choice = getattr(MaterialFrameEquivalence, "design_choice", None)
    assert choice and "material points" in choice


def test_gold_scores_one_and_garbage_scores_zero():
    for level in (0, 2, 5, 6):
        t = _task(level)
        for _ in range(5):
            ex = t.generate_example()
            assert ex.answer in ("Yes", "No")
            assert t.score_answer(ex.answer, ex) == 1.0
            assert t.score_answer("", ex) == 0.0
            assert t.score_answer("junk", ex) == 0.0
            assert t.score_answer("Yes" if ex.answer == "No" else "No", ex) == 0.0


def test_labels_balanced_over_many_samples():
    answers = {"Yes": 0, "No": 0}
    t = _task(0)
    for _ in range(200):
        answers[t.generate_example().answer] += 1
    total = answers["Yes"] + answers["No"]
    assert total == 200
    assert 0.35 < answers["Yes"] / total < 0.65


def test_reproducible_under_fixed_seed():
    a = []
    random.seed(1234)
    t = _task(3)
    for _ in range(5):
        a.append((t.generate_example().prompt, t.generate_example().answer))
    b = []
    random.seed(1234)
    t2 = _task(3)
    for _ in range(5):
        b.append((t2.generate_example().prompt, t2.generate_example().answer))
    assert a == b


def test_metadata_json_serializable():
    t = _task(5)
    import json
    ex = t.generate_example()
    json.dumps(dict(ex.metadata))


def test_difficulty_changes_config():
    t = MaterialFrameEquivalence()
    t.config.set_level(0)
    c0 = t.config.n_points
    t.config.set_level(6)
    assert t.config.n_points > c0
