import random

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.parametric_root_stability.parametric_root_stability import (
    ParametricRootStability,
    score_answer,
)


def _gold(entry):
    return entry.metadata["gold"]


def test_basic_generation_and_score():
    random.seed(0)
    task = ParametricRootStability()
    task.config.set_level(0)
    for _ in range(20):
        e = task.generate_example()
        assert score_answer(e.answer, e) == 1.0


def test_junk_rejected():
    random.seed(1)
    task = ParametricRootStability()
    e = task.generate_example()
    for bad in ("", "garbage", "??", "x", "[-5,5]" if e.metadata["gold"] != "[-5,5]" else "[-3,3]"):
        assert score_answer(bad, e) < 1.0


def test_levels_survive():
    task = ParametricRootStability()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(5):
            e = task.generate_example()
            assert score_answer(e.answer, e) == 1.0


def test_score_answer_no_self():
    # score_answer must raise on attribute access; call with a mock that raises
    class Mock:
        def __getattr__(self, name):
            raise AttributeError(name)

    random.seed(2)
    task = ParametricRootStability()
    e = task.generate_example()
    m = Mock()
    m.metadata = e.metadata
    assert score_answer(e.answer, m) == 1.0
