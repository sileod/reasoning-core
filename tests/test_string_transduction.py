from reasoning_core import list_tasks
from reasoning_core.tasks.string_transduction import StringTransduction, StringTransductionConfig


def test_string_transduction_registers_and_scores():
    assert "string_transduction" in list_tasks()
    assert "diff_prediction" not in list_tasks()
    task = StringTransduction()
    for _ in range(20):
        problem = task.generate_example(max_tokens=0)
        assert problem.answer
        assert task.score_answer(problem.answer, problem) == 1


def test_string_transduction_edit_mode():
    task = StringTransduction(StringTransductionConfig(edit_rate=1.0))
    problem = task.generate_example(max_tokens=0)
    assert problem.metadata.mode == "edit"
    assert problem.metadata.edits
    assert "Edits:" in problem.prompt
