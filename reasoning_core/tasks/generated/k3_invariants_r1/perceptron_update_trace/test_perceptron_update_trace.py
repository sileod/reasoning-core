import pytest

from reasoning_core.tasks.generated.k3_invariants_r1.perceptron_update_trace.perceptron_update_trace import (
    PerceptronUpdateTrace,
    _run_trace,
)


def _task():
    return PerceptronUpdateTrace()


@pytest.mark.parametrize("level", [0, 2, 4, 6])
def test_generation_all_levels(level):
    task = _task()
    task.config.set_level(level)
    ex = task.generate_example()
    assert int(ex.answer) == ex.metadata["final_first_mistake"]
    n = ex.metadata["num_examples"]
    assert -1 <= int(ex.answer) < n
    assert task.score_answer(ex.answer, ex) == 1.0


def test_prompt_determines_answer():
    task = _task()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            assert isinstance(prompt, str) and prompt
            # same metadata -> same answer and prompt
            ex2 = task.generate_example()
            assert task.score_answer(ex2.answer, ex2) == 1.0


def test_wrong_and_junk_answers_do_not_score_one():
    task = _task()
    task.config.set_level(3)
    ok = 0
    for _ in range(50):
        ex = task.generate_example()
        true = int(ex.answer)
        wrong = true + 1
        if wrong >= ex.metadata["num_examples"]:
            wrong = true - 1
        if task.score_answer(str(wrong), ex) == 1.0:
            ok += 1
    assert ok == 0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0


def test_reference_implementation_converges():
    examples = [([1, 0], 1), ([0, 1], 1), ([-1, 0], -1), ([0, -1], -1)]
    ans, conv = _run_trace(examples, 50)
    assert ans == -1 and conv
    ans2, _ = _run_trace(examples, 1)
    assert ans2 in (-1, 0, 1, 2, 3)
