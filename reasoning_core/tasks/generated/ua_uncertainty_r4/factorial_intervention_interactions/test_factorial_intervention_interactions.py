import random

from reasoning_core.tasks.generated.ua_uncertainty_r4.factorial_intervention_interactions.factorial_intervention_interactions import (
    FactorialInterventionInteractions,
)


def test_roundtrip_scores_one():
    task = FactorialInterventionInteractions()
    for _ in range(20):
        entry = task.generate_entry()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_multiple_levels_survive():
    for level in range(7):
        task = FactorialInterventionInteractions()
        task.config.set_level(level)
        for _ in range(5):
            entry = task.generate_entry()
            assert int(entry.answer) is not None
            assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_and_empty_score_zero():
    task = FactorialInterventionInteractions()
    entry = task.generate_entry()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("not a number", entry) == 0.0


def test_generation_deterministic_under_seed():
    random.seed(525660630)
    t1 = FactorialInterventionInteractions()
    a = [t1.generate_entry().answer for _ in range(10)]
    random.seed(525660630)
    t2 = FactorialInterventionInteractions()
    b = [t2.generate_entry().answer for _ in range(10)]
    assert a == b


def test_metadata_json_serializable():
    import json

    task = FactorialInterventionInteractions()
    entry = task.generate_entry()
    json.dumps(entry.metadata)


def test_answer_not_readable_off_surface():
    task = FactorialInterventionInteractions()
    seen = set()
    for _ in range(15):
        entry = task.generate_entry()
        seen.add(int(entry.answer))
    assert len(seen) > 1
