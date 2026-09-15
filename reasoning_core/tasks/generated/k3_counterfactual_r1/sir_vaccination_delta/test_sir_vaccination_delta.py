import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_counterfactual_r1.sir_vaccination_delta.sir_vaccination_delta import (
    SirVaccinationDelta,
    _parse_answer,
)


def _make_entry(task_level):
    t = SirVaccinationDelta()
    t.config.set_level(task_level)
    return t.generate_example()


def test_gold_scores_one_level0():
    task = SirVaccinationDelta()
    task.config.set_level(0)
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_gold_scores_one_all_levels():
    task = SirVaccinationDelta()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0, level


def test_answer_structure_and_domain():
    task = SirVaccinationDelta()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        a, b, d = _parse_answer(ex.answer)
        n = ex.metadata["final_runA"]
        assert 1 <= a <= len(ex.metadata["graph"])
        assert 0 <= b < a
        assert d >= 0
        assert a == ex.metadata["final_runA"]
        assert b == ex.metadata["final_runB"]
        assert d == ex.metadata["first_diff_day"]


def test_wrong_answers_fail():
    task = SirVaccinationDelta()
    task.config.set_level(0)
    ex = task.generate_example()
    assert task.score_answer("0 0 0", ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer(junk, ex) == 0.0


def test_junk_and_empty_do_not_score():
    task = SirVaccinationDelta()
    task.config.set_level(2)
    ex = task.generate_example()
    assert task.score_answer("   ", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0
    assert task.score_answer("1 2", ex) == 0.0
    assert task.score_answer("1 2 3 4", ex) == 0.0


junk = "not an answer"


def test_dedup_key_stable():
    task_a = SirVaccinationDelta()
    task_a.config.set_level(3)
    ex_a = task_a.generate_example()
    key_a = task_a.deduplication_key(ex_a)
    assert isinstance(key_a, str) and key_a
