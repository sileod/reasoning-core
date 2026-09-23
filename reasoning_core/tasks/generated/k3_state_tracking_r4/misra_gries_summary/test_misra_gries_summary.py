import random

from reasoning_core.tasks.generated.k3_state_tracking_r4.misra_gries_summary.misra_gries_summary import (
    MisraGriesSummary,
    run_misra_gries,
    summarize_table,
)


def test_generate_and_score():
    task = MisraGriesSummary()
    for _ in range(30):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_majority_counter_undershoots():
    task = MisraGriesSummary()
    for _ in range(30):
        entry = task.generate_example()
        m = entry.metadata
        table = run_misra_gries(m["stream"], m["k"])
        assert table[m["majority"]] < m["m_count"]


def test_score_balanced_and_balances():
    task = MisraGriesSummary()
    yes = no = 0
    for _ in range(200):
        entry = task.generate_example()
        if entry.metadata["can_be_majority"]:
            yes += 1
        else:
            no += 1
    assert yes > 0 and no > 0


def test_wrong_answers_score_low():
    task = MisraGriesSummary()
    for _ in range(30):
        entry = task.generate_example()
        _ = entry
        # A wrong majority label for the opposite case scores 0.
        flipped = "none|no" if entry.metadata["can_be_majority"] else "none|yes"
        assert task.score_answer(flipped, entry) == 0.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("a=1|maybe", entry) == 0.0


def test_summarize_table_ordering():
    assert summarize_table({}) == "none"
    assert summarize_table({3: 2, 1: 5}) == "1=5 3=2"


def test_run_misra_gries_rules():
    # increment on hit
    assert run_misra_gries([1, 1], 2) == {1: 2}
    # place new counter while under budget
    assert run_misra_gries([1, 2], 2) == {1: 1, 2: 1}
    # decrement-all + evict when full
    assert run_misra_gries([1, 2, 3], 2) == {}
