import random

import pytest

from reasoning_core.tasks.constraint_satisfaction import ConstraintSatisfaction, ConstraintSatisfactionConfig


def test_constraint_satisfaction_modes_generate_and_score():
    random.seed(1)
    for mode in ("attribute", "grid", "linear"):
        task = ConstraintSatisfaction(ConstraintSatisfactionConfig(model_mode=mode, n_vars=3, n_constraints=4))
        problem = task.generate_example(max_tokens=0)
        assert problem.metadata.model_mode == mode
        assert task.score_answer(problem.answer, problem) == 1


def test_constraint_satisfaction_finite_prompts_are_short():
    random.seed(2)
    for mode in ("attribute", "grid"):
        task = ConstraintSatisfaction(ConstraintSatisfactionConfig(model_mode=mode, n_vars=3, n_constraints=4))
        problem = task.generate_example(max_tokens=0)
        assert 3 <= len(problem.metadata.clues)
        assert "Answer with one" in problem.prompt


def test_grid_relational_clues_are_required_and_query_line_has_no_facts():
    random.seed(7)
    problem = ConstraintSatisfaction(ConstraintSatisfactionConfig(model_mode="grid", n_vars=3)).generate_entry()
    qr, qc = problem.metadata.query
    assert problem.metadata.relational_clues_required
    assert any(" < " in clue or " > " in clue for clue in problem.metadata.clues)
    for clue in problem.metadata.clues:
        if " = " in clue:
            assert not clue.startswith(f"r{qr}c")
            assert f"c{qc} =" not in clue


def test_linear_unsat_uses_the_configured_constraint_budget():
    for seed in range(5):
        config = ConstraintSatisfactionConfig(
            seed=seed,
            model_mode="linear",
            n_vars=3,
            n_constraints=6,
            unsat_prob=1.0,
            max_tries=256,
        )
        random.seed(seed)
        problem = ConstraintSatisfaction(config).generate_entry()

        assert problem.answer == "UNSAT"
        assert len(problem.metadata.constraints) == config.n_constraints


def test_lex_all_is_normalized_and_scored_as_enumeration():
    random.seed(3)
    task = ConstraintSatisfaction(ConstraintSatisfactionConfig(
        model_mode="linear", solve_mode="lex_all", unsat_prob=0, max_solutions=256,
    ))
    problem = task.generate_entry()
    assert problem.metadata.solve_mode == "all"
    assert task.score_answer(problem.answer, problem) == 1


def test_all_overflow_regenerates_instead_of_changing_objective():
    random.seed(4)
    task = ConstraintSatisfaction(ConstraintSatisfactionConfig(
        model_mode="linear", solve_mode="all", max_solutions=1, max_tries=256,
    ))
    problem = task.generate_entry()
    assert problem.metadata.solve_mode == "all"


@pytest.mark.parametrize("field,value", [
    ("solve_mode", "other"), ("model_mode", "other"), ("coef_bound", 0),
    ("max_solutions", 0), ("grid_width", -1), ("unsat_prob", 2),
])
def test_invalid_config_is_rejected(field, value):
    config = ConstraintSatisfactionConfig(**{field: value})
    with pytest.raises(ValueError):
        ConstraintSatisfaction(config)
