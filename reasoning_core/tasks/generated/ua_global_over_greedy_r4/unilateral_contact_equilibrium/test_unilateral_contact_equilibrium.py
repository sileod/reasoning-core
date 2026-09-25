import random

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.unilateral_contact_equilibrium.unilateral_contact_equilibrium import (
    UnilateralContactEquilibrium,
)


def _random_task():
    random.seed(1140349348)
    return UnilateralContactEquilibrium()


def test_gold_scores_one():
    task = _random_task()
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1.0


def test_positive_answer_domain():
    task = _random_task()
    for _ in range(200):
        entry = task.generate_entry()
        from fractions import Fraction

        assert Fraction(entry.answer) > 0


def test_junk_score_zero():
    task = _random_task()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("banana", entry) == 0.0
    assert task.score_answer("None", entry) == 0.0


def test_levels_generate():
    task = _random_task()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_entry()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_equivalent_fraction_forms():
    task = _random_task()
    entry = task.generate_example()
    from fractions import Fraction

    f = Fraction(entry.answer)
    assert task.score_answer(str(f), entry) == 1.0
    assert task.score_answer(str(0), entry) == 0.0
    assert task.score_answer(float(f), entry) == 0.0


def test_no_constant_answer_per_level():
    task = _random_task()
    for level in range(7):
        task.config.set_level(level)
        answers = set()
        for _ in range(120):
            e = task.generate_entry()
            answers.add(e.answer)
        assert len(answers) >= 10, "level %d too few distinct answers" % level


def test_metadata_json_serializable():
    import json

    task = _random_task()
    for _ in range(20):
        entry = task.generate_entry()
        json.dumps(entry.metadata)
