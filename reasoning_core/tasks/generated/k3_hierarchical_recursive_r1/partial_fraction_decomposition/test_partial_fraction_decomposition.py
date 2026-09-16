from fractions import Fraction

import pytest

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.partial_fraction_decomposition.partial_fraction_decomposition import (
    PartialFractionDecomposition,
)


def test_generate_render_score_roundtrip():
    task = PartialFractionDecomposition()
    for _ in range(50):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        assert prompt
        assert len(entry.metadata["answer"]) >= 1
        assert task.score_answer(entry.answer, entry) == 1.0


def test_num_degree_one_less_than_den():
    task = PartialFractionDecomposition()
    for _ in range(50):
        entry = task.generate_example()
        lin = entry.metadata["linear_factors"]
        quad = entry.metadata["quad_factors"]
        den_deg = sum(e for _, e in lin) + sum(2 * e for _, _, e in quad)
        num_deg = len(entry.metadata["numerator"]) - 1
        assert num_deg == den_deg - 1


def test_quadratic_has_constant_and_linear_terms():
    task = PartialFractionDecomposition()
    seen_quad = False
    for _ in range(200):
        entry = task.generate_example()
        for slot in entry.metadata["slots"]:
            if "A_" in slot and "x" in slot:
                seen_quad = True
    assert seen_quad


def test_random_answers_do_not_score_one():
    task = PartialFractionDecomposition()
    for _ in range(50):
        entry = task.generate_example()
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("garbage", entry) == 0.0
        wrong = ",".join("0" for _ in entry.metadata["answer"])
        assert task.score_answer(wrong, entry) == 0.0


def test_difficulty_scaling():
    task = PartialFractionDecomposition()
    l0 = task.config.n_linear
    task.config.set_level(5)
    assert task.config.n_linear >= l0
    assert task.config.max_mult > 0


def test_all_levels_generate():
    task = PartialFractionDecomposition()
    for level in range(0, 7):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_exact_rationals():
    task = PartialFractionDecomposition()
    for _ in range(50):
        entry = task.generate_example()
        for val in entry.metadata["answer"]:
            Fraction(val)
