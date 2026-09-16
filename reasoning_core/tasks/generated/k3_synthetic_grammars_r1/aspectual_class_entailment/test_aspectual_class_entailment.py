import random

from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.aspectual_class_entailment.aspectual_class_entailment import (
    AspectualClassEntailment,
    CLASS_LABEL,
    VERDICTS,
    IN_OK,
    FOR_OK,
    CLASSES,
)


def test_gold_scores_one():
    task = AspectualClassEntailment()
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_do_not_score_one():
    task = AspectualClassEntailment()
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("garbage", ex) == 0.0
        assert task.score_answer(ex.answer + " x", ex) == 0.0


def test_answer_matches_class_and_verdict_schema():
    task = AspectualClassEntailment()
    for _ in range(50):
        ex = task.generate_example()
        cls = ex.metadata["cls"]
        label = CLASS_LABEL[cls]
        v = VERDICTS[cls]
        expected = f"{label} " + " ".join("yes" if x else "no" for x in v)
        assert ex.answer == expected
        assert in_ok_label(cls, v) == IN_OK[cls]
        assert for_ok_label(cls, v) == FOR_OK[cls]


def in_ok_label(cls, v):
    return bool(v[0])


def for_ok_label(cls, v):
    return bool(v[1])


def test_all_classes_reachable():
    task = AspectualClassEntailment()
    random.seed(7)
    seen = set()
    for _ in range(200):
        ex = task.generate_entry()
        seen.add(ex.metadata["cls"])
    assert seen == set(CLASSES)


def test_label_distribution_balanced():
    task = AspectualClassEntailment()
    random.seed(11)
    counts = {c: 0 for c in CLASSES}
    n = 1000
    for _ in range(n):
        ex = task.generate_entry()
        counts[ex.metadata["cls"]] += 1
    for c in CLASSES:
        assert counts[c] > n // 4 - n // 10, (c, counts[c])


def test_no_constant_answer_from_predicate_order():
    task = AspectualClassEntailment()
    random.seed(3)
    answers = set()
    for _ in range(400):
        ex = task.generate_entry()
        answers.add(ex.answer)
    assert len(answers) >= 4


def test_prompt_mentions_predicate_and_format():
    task = AspectualClassEntailment()
    random.seed(5)
    for _ in range(10):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        assert ex.metadata["predicate"] in prompt
        assert "S, A, Acc, or Ach" in prompt
        assert task.score_answer(ex.answer, ex) == 1.0
