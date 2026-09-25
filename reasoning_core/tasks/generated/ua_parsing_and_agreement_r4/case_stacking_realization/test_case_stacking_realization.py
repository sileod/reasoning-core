import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_parsing_and_agreement_r4.case_stacking_realization.case_stacking_realization import (
    CaseStackingRealization,
    _realized,
    _VOWELS,
    _CLASSES,
    _OWNCASES,
)


def test_gold_answer_scores_one():
    task = CaseStackingRealization()
    random.seed(2267388306)
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_matches_independent_reconstruction():
    task = CaseStackingRealization()
    random.seed(1)
    for _ in range(100):
        ex = task.generate_example()
        md = ex.metadata
        left_classes = [c for c in md["classes"][: md["j"] - 1]]
        expected = _realized(md["query_case"], md["query_class"],
                             md["query_tail"], left_classes)
        assert ex.answer == expected


def test_instance_lies_below_stack_depth_cap():
    task = CaseStackingRealization()
    random.seed(2)
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            left_poss = ex.metadata["j"] - 1
            assert 0 <= left_poss <= 4


def test_constant_guess_fails():
    task = CaseStackingRealization()
    random.seed(3)
    answers = {task.generate_example().answer for _ in range(120)}
    assert len(answers) > 40


def test_fusion_rule_is_applied():
    assert _realized("NOM", "A", "a", []) == "na"
    assert _realized("NOM", "B", "a", ["A"]) == "run"
    assert _realized("NOM", "A", "s", []) == "na"
    assert _realized("DAT", "A", "s", []) == "jia"
    assert _realized("NOM", "A", "s", ["B"]) == "nar"
