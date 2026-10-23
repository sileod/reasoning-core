import pytest

from reasoning_core.evaluation.encoder import task_items
from reasoning_core.evaluation.metrics import EvalExample, score_mcq
from reasoning_core.utils.hf_sample import sample_rows


def test_negatives_come_from_the_same_task_and_level_and_never_equal_the_gold():
    rows = [{"task": t, "level": l, "prompt": f"{t}{l}{i}", "answer": f"{t}-{l}-{i}"}
            for t in ("a", "b") for l in (0, 1) for i in range(5)]
    items = task_items(rows, negatives=3, seed=1)
    for task, got in items.items():
        assert len(got) == 10
        for prompt, choices, gold in got:
            level = prompt[1]
            assert len(choices) == 4 and len(set(choices)) == 4
            assert choices[gold] == f"{task}-{level}-{prompt[2]}"
            assert all(c.startswith(f"{task}-{level}-") for c in choices)


def test_a_group_with_one_answer_contributes_no_items():
    rows = [{"task": "a", "level": 0, "prompt": str(i), "answer": "same"} for i in range(3)]
    assert task_items(rows, negatives=3) == {}


def test_score_mcq_takes_any_cost_lower_is_better():
    examples = [EvalExample("q", "x", ("x", "y"), 0), EvalExample("q", "y", ("x", "y"), 1)]
    result = score_mcq(examples, lambda ex: [0.0, 1.0])      # always picks choice 0
    assert result["accuracy"] == 0.5 and result["margin"] == 0.0


def test_sample_rows_needs_a_pinned_revision():
    with pytest.raises(ValueError):
        sample_rows("tasksource/tasksource_dpo_pairs", "main", n=10)
