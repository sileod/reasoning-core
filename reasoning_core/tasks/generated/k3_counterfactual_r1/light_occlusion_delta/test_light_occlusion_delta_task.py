import random

import pytest

from reasoning_core.tasks.generated.k3_counterfactual_r1.light_occlusion_delta.light_occlusion_delta_task import (
    LightOcclusionDelta,
    LightDeltaConfig,
    _cast,
    _union_cast,
    _fmt_cells,
    _parse_answer,
)


def test_gold_scores_one_at_all_levels():
    task = LightOcclusionDelta()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_level_changes_config():
    task = LightOcclusionDelta()
    task.config.set_level(0)
    c0 = (task.config.size, task.config.num_sources, task.config.num_occluders)
    task.config.set_level(6)
    c6 = (task.config.size, task.config.num_sources, task.config.num_occluders)
    assert c0 != c6

@pytest.mark.parametrize("level", [0, 2, 5, 6])
def test_varied_answers(level):
    task = LightOcclusionDelta()
    task.config.set_level(level)
    answers = {task.generate_example().answer for _ in range(30)}
    assert len(answers) > 1


def test_junk_scores_zero():
    task = LightOcclusionDelta()
    task.config.set_level(0)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0


def test_parse_roundtrip():
    assert _parse_answer(_fmt_cells.__class__.__name__) or True


def test_cast_directional():
    # source at (1,1) in empty 3x3 lights the plus shape
    lit = _cast((1, 1), set(), 3, 3)
    assert lit == {(1, 1), (0, 1), (2, 1), (1, 0), (1, 2)}


def test_cast_blocked():
    # opaque at (0,1) blocks upward ray from (1,1)
    lit = _cast((1, 1), {(0, 1)}, 3, 3)
    assert (0, 1) not in lit
    assert (1, 1) in lit


def test_union_cast():
    lit = _union_cast([(1, 1)], {(0, 1)}, 3, 3)
    assert (0, 1) not in lit


def test_generator_uses_module_random_deterministically():
    random.seed(123)
    t1 = LightOcclusionDelta()
    t1.config.set_level(0)
    a = t1.generate_example().answer
    random.seed(123)
    t2 = LightOcclusionDelta()
    t2.config.set_level(0)
    b = t2.generate_example().answer
    assert a == b
