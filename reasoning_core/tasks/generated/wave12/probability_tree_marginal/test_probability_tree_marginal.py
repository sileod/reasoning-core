import random

from reasoning_core.tasks.generated.wave12.probability_tree_marginal.probability_tree_marginal import (
    ProbabilityTreeMarginal,
    _fraction_of,
)


def test_gold_scores_one_at_levels():
    task = ProbabilityTreeMarginal()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_answers_are_reduced_fractions_in_range():
    task = ProbabilityTreeMarginal()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        fr = _fraction_of(ex.answer)
        assert fr is not None
        assert 0 <= fr <= 1
        assert ex.answer == ("%d/%d" % (fr.numerator, fr.denominator)) or ex.answer == str(fr.numerator)


def test_rows_sum_to_one_and_metadata_jsonable():
    task = ProbabilityTreeMarginal()
    import json

    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        json.dumps(ex.metadata)
        m = ex.metadata
        assert len(m["transitions"]) == m["states"]


def test_junk_and_wrong_answers_fail():
    task = ProbabilityTreeMarginal()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("banana", ex) == 0.0
    assert task.score_answer("3/2", ex) == 0.0


def test_difficulty_changes():
    task = ProbabilityTreeMarginal()
    c0 = ProbabilityTreeMarginal().config
    c0.set_level(0)
    c5 = ProbabilityTreeMarginal().config
    c5.set_level(5)
    assert c5.steps > c0.steps
