import numpy as np

from reasoning_core.tasks.generated.ua_invariants_r4.quadratic_energy_signature.quadratic_energy_signature import (
    QuadraticEnergySignature,
    _matrix_signature,
)


def test_scoring_roundtrip():
    task = QuadraticEnergySignature()
    for _ in range(50):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("x,y", entry) == 0.0


def test_gold_is_correct():
    task = QuadraticEnergySignature()
    sig = _matrix_signature
    for _ in range(50):
        entry = task.generate_example()
        matrix = np.array(entry.metadata["matrix"], dtype=float)
        assert sig(matrix) == tuple(entry.metadata["signature"])


def test_difficulty_changes():
    task = QuadraticEnergySignature()
    c0 = task.config.set_level(0)
    c6 = task.config.set_level(6)
    assert c6.size >= c0.size


def test_all_levels_generate():
    task = QuadraticEnergySignature()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(5):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0
