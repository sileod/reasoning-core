import random

from reasoning_core.tasks.generated.k3_verification_repair_r1.euler_tour_intervals.euler_tour_intervals import (
    EulerTourIntervals,
)

TASK = EulerTourIntervals()


def test_yes_no_answers():
    random.seed(1475571465)
    for _ in range(50):
        entry = TASK.generate_entry()
        assert entry.answer in ("yes", "no")


def test_gold_scores_one():
    random.seed(1475571465)
    for _ in range(50):
        entry = TASK.generate_entry()
        assert TASK.score_answer(entry.answer, entry) == 1.0


def test_wrong_scores_zero():
    random.seed(2)
    entry = TASK.generate_entry()
    wrong = "yes" if entry.answer == "no" else "no"
    assert TASK.score_answer(wrong, entry) == 0.0
    assert TASK.score_answer("", entry) == 0.0
    assert TASK.score_answer("maybe", entry) == 0.0


def test_answer_matches_stamp_verifier():
    random.seed(1475571465)
    for _ in range(200):
        entry = TASK.generate_entry()
        tin = {int(k): v for k, v in entry.metadata["tin"].items()}
        tout = {int(k): v for k, v in entry.metadata["tout"].items()}
        a, b = entry.metadata["query"]
        is_anc = tin[a] <= tin[b] <= tout[a]
        expected = "yes" if is_anc else "no"
        assert entry.answer == expected, (entry.answer, expected)


def test_parent_list_well_formed():
    random.seed(1475571465)
    for _ in range(100):
        entry = TASK.generate_entry()
        parent = entry.metadata["parent_list"]
        n = entry.metadata["n_nodes"]
        assert len(parent) == n
        assert parent[0] is None
        for k in range(1, n):
            assert parent[k] is not None and 0 <= parent[k] < k


def test_difficulty_changes():
    random.seed(1475571465)
    TASK.config.set_level(0)
    l0 = TASK.config.n_nodes
    TASK.config.set_level(6)
    l6 = TASK.config.n_nodes
    assert l6 > l0
