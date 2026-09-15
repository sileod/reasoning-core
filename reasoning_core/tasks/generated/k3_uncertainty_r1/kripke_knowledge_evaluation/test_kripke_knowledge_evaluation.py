import random

from reasoning_core.tasks.generated.k3_uncertainty_r1.kripke_knowledge_evaluation.kripke_knowledge_evaluation import (
    KripkeKnowledgeEvaluation,
)


def test_gold_score():
    task = KripkeKnowledgeEvaluation()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_answers():
    task = KripkeKnowledgeEvaluation()
    for _ in range(10):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("banana", ex) == 0.0
        assert task.score_answer(None, ex) == 0.0


def test_label_balance():
    task = KripkeKnowledgeEvaluation()
    ones = 0
    total = 0
    for _ in range(60):
        ex = task.generate_example()
        total += 1
        if ex.answer == "True":
            ones += 1
    frac = ones / total
    assert 0.2 < frac < 0.8, frac


def test_levels_produce():
    task = KripkeKnowledgeEvaluation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(3):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
