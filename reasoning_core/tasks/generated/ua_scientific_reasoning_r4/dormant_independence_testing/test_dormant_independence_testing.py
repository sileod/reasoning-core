import pytest

from reasoning_core.template import Task
from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.dormant_independence_testing.dormant_independence_testing import (
    DormantIndependenceTesting,
    _compute,
    _gold,
)


def test_generate_render_score_roundtrip():
    task = DormantIndependenceTesting()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0
    assert task.render_prompt(ex.metadata)
    assert "!=" in ex.answer


def test_junk_scores_zero():
    task = DormantIndependenceTesting()
    ex = task.generate_example()
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("1/1 != 1/1", ex) == 0.0


def test_difficulty_changes_config():
    task = DormantIndependenceTesting()
    c0 = task.config.n_units
    task.config.set_level(6)
    assert task.config.n_units != c0
    assert task.config.m_states >= 2


def test_all_levels_generate_and_violate():
    for lvl in (0, 1, 2, 3, 4, 5, 6):
        task = DormantIndependenceTesting()
        task.config.set_level(lvl)
        ex = task.generate_entry()
        cells = ex.metadata["cells"]
        res = _compute(cells, ex.metadata["xout"])
        assert any(n != d for n, d in res), f"level {lvl} had no violation"
        assert ex.metadata["answer"] == _gold(cells, ex.metadata["xout"])


def test_validate():
    task = DormantIndependenceTesting()
    task.validate()


def test_not_task_name():
    assert "Task" not in type(DormantIndependenceTesting()).__name__
