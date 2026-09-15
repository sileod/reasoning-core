from reasoning_core.tasks.generated.k3_uncertainty_r1.iterated_dominance_elimination.iterated_dominance_elimination import (
    IteratedDominanceElimination,
)


def test_generate_and_score():
    task = IteratedDominanceElimination()
    for _ in range(30):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_difficulty_changes():
    task = IteratedDominanceElimination()
    c0 = task.config
    task.config.set_level(6)
    assert task.config.rows >= c0.rows
    assert task.config.max_removals >= c0.max_removals


def test_surviving_sets_nonempty():
    task = IteratedDominanceElimination()
    for _ in range(30):
        x = task.generate_example()
        m = x.metadata
        assert len(m["surviving_rows"]) >= 1
        assert len(m["surviving_cols"]) >= 1
        assert m["removed_count"] >= task.config.max_removals


def test_junk_answers_fail():
    task = IteratedDominanceElimination()
    x = task.generate_example()
    assert task.score_answer("junk", x) == 0.0
    assert task.score_answer("", x) == 0.0
