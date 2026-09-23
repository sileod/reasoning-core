import random

from reasoning_core.tasks.generated.k3_formal_logic_r4.ownership_lifeline_transfer.ownership_lifeline_transfer import (
    OwnershipLifelineTransfer,
    _first_illegal,
)


def _gold(entry):
    return f"{entry.metadata['illegal_index'] + 1}: {entry.metadata['rule']}"


def test_gold_answer_scores_one():
    task = OwnershipLifelineTransfer()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config = type(task.config)()
        task.config.set_level(level)
        entry = task.generate_example()
        assert entry.answer == _gold(entry)
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_index_in_domain():
    task = OwnershipLifelineTransfer()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config = type(task.config)()
        task.config.set_level(level)
        entry = task.generate_example()
        idx = int(entry.answer.split(":")[0])
        assert 1 <= idx <= len(entry.metadata["events"])


def test_first_illegal_is_at_gold_index():
    task = OwnershipLifelineTransfer()
    for _ in range(60):
        entry = task.generate_example()
        owner = entry.metadata["initial_owner"]
        fi = _first_illegal(entry.metadata["events"], owner)
        assert fi is not None
        assert fi[0] == entry.metadata["illegal_index"]
        assert fi[1] == entry.metadata["rule"]


def test_junk_scores_zero():
    task = OwnershipLifelineTransfer()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("not a number", entry) == 0.0
    assert task.score_answer(None, entry) == 0.0
    assert task.score_answer("moved-value", entry) == 0.0
    assert task.score_answer("0: moved-value", entry) == 0.0
    assert task.score_answer("999: borrow-in-use", entry) == 0.0
    assert task.score_answer("banana: moved-value", entry) == 0.0


def test_answers_vary():
    task = OwnershipLifelineTransfer()
    random.seed(7)
    seen = set()
    for _ in range(60):
        entry = task.generate_example()
        seen.add(entry.answer)
    assert len(seen) > 1


def test_rules_and_indices_vary():
    task = OwnershipLifelineTransfer()
    random.seed(11)
    rules = set()
    indices = set()
    for _ in range(80):
        entry = task.generate_example()
        idx, rule = entry.answer.split(":")
        rules.add(rule.strip())
        indices.add(int(idx))
    assert len(rules) >= 2
    assert len(indices) >= 3
