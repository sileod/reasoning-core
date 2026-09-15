import random

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.lights_out_press_set.lights_out_press_set import (
    LightsOutPressSet,
    _is_consistent,
    _parse_answer,
    _toggle_matrix,
    _unique_solve,
)
import numpy as np


def test_summary_and_design_choice():
    assert isinstance(LightsOutPressSet.summary, str)
    assert isinstance(LightsOutPressSet.design_choice, str)


def test_validate_all_levels():
    random.seed(2302342651)
    for level in (0, 1, 2, 3, 4, 5, 6):
        task = LightsOutPressSet()
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1
        assert task.score_answer("", ex) == 0
        assert task.score_answer("not valid", ex) == 0


def test_config_scales():
    c0 = LightsOutPressSet.config_cls()
    c0.set_level(0)
    c6 = LightsOutPressSet.config_cls()
    c6.set_level(6)
    assert c6.max_side > c0.max_side


def test_solvable_answer_is_reproducible():
    random.seed(7)
    task = LightsOutPressSet()
    ex = task.generate_example()
    if ex.metadata["solvable"]:
        mat = _toggle_matrix(ex.metadata["rows"], ex.metadata["cols"])
        flat = np.asarray(ex.metadata["flat_pattern"], dtype=np.int8)
        press = ex.metadata["press"]
        assert press is not None and sorted(press) == press
        indicator = np.zeros(ex.metadata["n_cells"], dtype=np.int8)
        indicator[list(press)] = 1
        assert np.array_equal((mat % 2) @ indicator % 2, flat)


def test_none_answer_is_inconsistent():
    random.seed(11)
    task = LightsOutPressSet()
    for _ in range(60):
        ex = task.generate_example()
        if not ex.metadata["solvable"]:
            mat = _toggle_matrix(ex.metadata["rows"], ex.metadata["cols"])
            flat = np.asarray(ex.metadata["flat_pattern"], dtype=np.int8)
            assert not _is_consistent(mat, flat)
            assert ex.answer == "NONE"
            return
    raise AssertionError("no NONE instance generated in 60 tries")


def test_parse_answer():
    assert _parse_answer("NONE", 10) == frozenset()
    assert _parse_answer("none", 10) == frozenset()
    assert _parse_answer("3 1 2", 10) == frozenset({1, 2, 3})
    assert _parse_answer("99", 10) is None
    assert _parse_answer("abc", 10) is None
    assert _parse_answer("", 10) is None


def test_balance_both_answers():
    random.seed(99)
    task = LightsOutPressSet()
    yes = no = 0
    for _ in range(80):
        ex = task.generate_example()
        if ex.metadata["solvable"]:
            yes += 1
        else:
            no += 1
    assert yes > 0 and no > 0
