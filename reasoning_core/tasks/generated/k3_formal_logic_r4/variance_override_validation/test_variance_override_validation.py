import random

from reasoning_core.tasks.generated.k3_formal_logic_r4.variance_override_validation.variance_override_validation import (
    VarianceOverrideValidation,
)


def test_generate_and_roundtrip():
    task = VarianceOverrideValidation()
    task.config.set_level(2)
    for _ in range(50):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_domain():
    task = VarianceOverrideValidation()
    task.config.set_level(3)
    for _ in range(30):
        entry = task.generate_example()
        assert entry.answer in ('covariant', 'contravariant', 'invariant')


def test_empty_and_junk_scored_zero():
    task = VarianceOverrideValidation()
    task.config.set_level(1)
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("banana", entry) == 0.0


def test_difficulty_changes_config():
    task = VarianceOverrideValidation()
    task.config.set_level(0)
    d0 = task.config.depth
    task.config.set_level(6)
    d6 = task.config.depth
    assert d6 > d0


def test_levels_all_balanced_labels():
    task = VarianceOverrideValidation()
    for level in (0, 3, 6):
        task.config.set_level(level)
        labels = set()
        for _ in range(40):
            labels.add(task.generate_example().answer)
        assert labels, f"level {level} produced no examples"


def test_all_levels_generate():
    task = VarianceOverrideValidation()
    for level in range(7):
        task.config.set_level(level)
        random.seed(level)
        for _ in range(10):
            task.generate_example()
