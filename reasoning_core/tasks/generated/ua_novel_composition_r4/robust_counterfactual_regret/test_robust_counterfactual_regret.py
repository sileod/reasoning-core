import pytest

from reasoning_core.tasks.generated.ua_novel_composition_r4.robust_counterfactual_regret.robust_counterfactual_regret import (
    RobustCounterfactualRegret,
    best_intervention_and_witness,
    worst_regret,
)


@pytest.fixture
def task():
    return RobustCounterfactualRegret()


def test_gold_scores_one(task):
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero(task):
    e = task.generate_example()
    assert task.score_answer("junk", e) == 0.0
    assert task.score_answer("", e) == 0.0
    assert task.score_answer(None, e) == 0.0
    assert task.score_answer("0 1 ", e) == 0.0


def test_gold_not_surface_readable(task):
    for _ in range(50):
        e = task.generate_example()
        costs = e.metadata["costs"]
        flat = [c for row in costs for c in row]
        bi, ws, _, _ = best_intervention_and_witness(costs)
        assert e.metadata["best_intervention"] == bi
        assert e.metadata["witness_scenario"] == ws
        ans = f"{bi} {ws}"
        assert ans == e.answer
        assert ans not in [str(x) for x in flat]


def test_witness_is_max_regret_scenario(task):
    for _ in range(50):
        e = task.generate_example()
        costs = e.metadata["costs"]
        bi = e.metadata["best_intervention"]
        ws = e.metadata["witness_scenario"]
        regret = worst_regret(costs)
        assert regret[bi][ws] == max(regret[bi])


def test_best_minimizes_worst_regret(task):
    for _ in range(50):
        e = task.generate_example()
        costs = e.metadata["costs"]
        bi = e.metadata["best_intervention"]
        regret = worst_regret(costs)
        worst = [max(row) for row in regret]
        assert worst[bi] == min(worst)


def test_regret_nonnegative(task):
    for _ in range(50):
        e = task.generate_example()
        costs = e.metadata["costs"]
        for row in worst_regret(costs):
            for v in row:
                assert isinstance(v, int)
                assert v >= 0


def test_tie_break_smallest_index(task):
    for _ in range(50):
        e = task.generate_example()
        costs = e.metadata["costs"]
        bi, ws, _, regret = best_intervention_and_witness(costs)
        worst = [max(row) for row in regret]
        assert bi == min(i for i in range(len(costs)) if worst[i] == min(worst))
        assert ws == min(s for s in range(len(costs[0])) if regret[bi][s] == max(regret[bi]))


def test_levels_differ(task):
    base = task.config.__dict__.copy()
    task.config.set_level(3)
    assert task.config.__dict__ != base


@pytest.mark.parametrize("level", list(range(7)))
def test_generates_all_levels(level):
    t = RobustCounterfactualRegret()
    t.config.set_level(level)
    answers = set()
    for _ in range(30):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0
        answers.add(e.answer)
    assert len(answers) > 1


def test_answer_space_diverse(task):
    answers = set()
    for _ in range(200):
        e = task.generate_example()
        answers.add(e.answer)
    assert len(answers) > 5
