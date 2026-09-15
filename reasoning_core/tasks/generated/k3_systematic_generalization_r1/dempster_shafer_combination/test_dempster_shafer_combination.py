import random
from fractions import Fraction

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.dempster_shafer_combination.dempster_shafer_combination import (
    DempsterShaferCombination, DempsterShaferConfig, _parse_frac, _combine, _fmt_set, FOCAL)

TASK_MODULE = "reasoning_core.tasks.generated.k3_systematic_generalization_r1.dempster_shafer_combination.dempster_shafer_combination"


def test_design_choice_and_meta():
    assert DempsterShaferCombination.design_choice.startswith(
        "Frame size fixed at 3 hypotheses")


def test_gold_scores():
    random.seed(123)
    task = DempsterShaferCombination()
    for _ in range(40):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_garbage():
    random.seed(7)
    task = DempsterShaferCombination()
    e = task.generate_example()
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("junk", e) == 0.0
    assert task.score_answer("3.7", e) == 0.0
    assert task.score_answer("x/y", e) == 0.0
    assert task.score_answer(e.answer + "1", e) == 0.0


def test_answer_in_unit_interval():
    for level in range(7):
        task = DempsterShaferCombination()
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_example()
            f = _parse_frac(e.answer)
            assert f is not None
            assert Fraction(0) <= f <= Fraction(1)


def test_answers_vary():
    random.seed(99)
    task = DempsterShaferCombination()
    answers = {task.generate_example().answer for _ in range(200)}
    assert len(answers) > 40


def test_both_variants_produced():
    random.seed(5)
    task = DempsterShaferCombination()
    variants = {task.generate_example().metadata.variant for _ in range(120)}
    assert variants == {"combine", "conflict"}


def test_combine_helper():
    c1 = {("A",): 1, ("B",): 1}
    c2 = {("A",): 2, ("C",): 2}
    pooled, conflict = _combine(c1, c2)
    assert conflict == 6
    assert pooled.get(("A",)) == 2
    assert _fmt_set(("A", "B")) == "{A,B}"


def test_level_change_changes_config():
    task = DempsterShaferCombination()
    c0 = task.config.denominator
    task.config.set_level(3)
    assert task.config.denominator > c0


def test_metadata_json_serializable():
    import json
    random.seed(2)
    task = DempsterShaferCombination()
    for _ in range(20):
        e = task.generate_example()
        json.dumps(dict(e.metadata))
