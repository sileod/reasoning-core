import random

import pytest

from reasoning_core.tasks.generated.k3_novel_composition_r1.session_type_projection.session_type_projection import (
    SessionConfig,
    SessionTypeProjection,
    _build,
    _dual,
    _project,
)


@pytest.fixture
def task():
    return SessionTypeProjection()


def test_generate_example_works(task):
    ex = task.generate_example()
    assert ex.answer in ("equal", "not")
    assert ex.metadata["target"] in ex.metadata["participants"]
    assert ex.metadata["answer"] == ex.answer


def test_gold_scores_one(task):
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_scores_zero(task):
    ex = task.generate_example()
    other = "equal" if ex.answer == "not" else "not"
    assert task.score_answer(other, ex) == 0.0


def test_empty_and_junk_zero(task):
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage input", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0
    assert task.score_answer(42, ex) == 0.0


def test_render_prompt_roundtrip(task):
    ex = task.generate_example()
    p = task.render_prompt(ex.metadata)
    assert "G =" in p
    assert "L =" in p
    assert str(ex.metadata["target"]) in p
    assert "equal" in p and "not" in p


def test_answer_balanced_across_levels():
    task = SessionTypeProjection()
    for level in (0, 3, 6):
        task.config.set_level(level)
        counts = {"equal": 0, "not": 0}
        for _ in range(60):
            ex = task.generate_example()
            counts[ex.answer] += 1
        assert counts["equal"] > 0 and counts["not"] > 0, (level, counts)


def test_dual_of_send_is_receive():
    assert _dual("P1 ! m", None) == "P1 ? m"
    assert _dual("P1 ? m", None) == "P1 ! m"


def test_projection_of_send_to_target():
    tree = ("!", "P1", "m")
    res, local = _project(tree, "P1")
    assert res == "type" and local == "P1 ! m"
    res, local = _project(tree, "P2")
    assert res == "type" and local == "end"


def test_difficulty_changes_config():
    cfg = SessionConfig()
    cfg.set_level(0)
    d0 = cfg.depth
    cfg.set_level(6)
    d6 = cfg.depth
    assert d6 > d0
    assert cfg.participants > 3


def test_all_levels_generate(task):
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        assert ex.answer in ("equal", "not")
