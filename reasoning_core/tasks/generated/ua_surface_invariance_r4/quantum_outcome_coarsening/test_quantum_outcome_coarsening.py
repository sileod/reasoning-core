import random

from reasoning_core.tasks.generated.ua_surface_invariance_r4.quantum_outcome_coarsening.quantum_outcome_coarsening import (
    QuantumOutcomeCoarsening,
    QuantumOutcomeCoarseningV1Config,
    _score_state,
)


def test_generate_and_score_every_level():
    task = QuantumOutcomeCoarsening()
    for level in range(7):
        task.config = QuantumOutcomeCoarseningV1Config()
        task.config.set_level(level)
        for _ in range(40):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = QuantumOutcomeCoarsening()
    task.config = QuantumOutcomeCoarseningV1Config()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("foo bar baz", ex) == 0.0
    assert task.score_answer("1/2", ex) == 0.0


def test_answer_is_valid_state():
    task = QuantumOutcomeCoarsening()
    task.config = QuantumOutcomeCoarseningV1Config()
    task.config.set_level(3)
    for _ in range(60):
        ex = task.generate_example()
        from fractions import Fraction
        vals = [Fraction(x) for x in ex.answer.split()]
        r00, r01, r11 = vals
        assert r00 + r11 == 1
        assert 0 <= r00 <= 1 and 0 <= r11 <= 1
        assert r00 * r11 >= r01 * r01


def test_distinct_answers_exist():
    task = QuantumOutcomeCoarsening()
    task.config = QuantumOutcomeCoarseningV1Config()
    task.config.set_level(0)
    answers = set()
    for _ in range(120):
        answers.add(task.generate_example().answer)
    assert len(answers) > 5


def test_difficulty_changes_config():
    c = QuantumOutcomeCoarseningV1Config()
    c.set_level(0)
    base = (c.max_abs, c.max_den)
    c2 = QuantumOutcomeCoarseningV1Config()
    c2.set_level(6)
    assert (c2.max_abs, c2.max_den) != base
    assert c2.max_abs > c.max_abs
