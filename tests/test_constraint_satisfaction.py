from reasoning_core.tasks.constraint_satisfaction import ConstraintSatisfaction, ConstraintSatisfactionConfig


def test_constraint_satisfaction_modes_generate_and_score():
    for mode in ("attribute", "grid", "linear"):
        task = ConstraintSatisfaction(ConstraintSatisfactionConfig(model_mode=mode, n_vars=3, n_constraints=4))
        problem = task.generate_example(max_tokens=0)
        assert problem.metadata.model_mode == mode
        assert task.score_answer(problem.answer, problem) == 1


def test_constraint_satisfaction_finite_prompts_are_short():
    for mode in ("attribute", "grid"):
        task = ConstraintSatisfaction(ConstraintSatisfactionConfig(model_mode=mode, n_vars=3, n_constraints=4))
        problem = task.generate_example(max_tokens=0)
        assert 4 <= len(problem.metadata.clues) <= 8
        assert "Answer with one" in problem.prompt
