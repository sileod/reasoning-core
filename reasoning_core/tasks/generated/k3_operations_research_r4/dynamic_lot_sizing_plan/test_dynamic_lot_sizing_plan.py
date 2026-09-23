import pytest

from reasoning_core.tasks.generated.k3_operations_research_r4.dynamic_lot_sizing_plan.dynamic_lot_sizing_plan import (
    DynamicLotSizingPlan,
    _plan_cost,
)


def test_gold_scoring_roundtrip():
    for level in (0, 2, 5, 6):
        task = DynamicLotSizingPlan()
        task.config.set_level(level)
        for _ in range(5):
            entry = task.generate_entry()
            assert entry.answer == " ".join(str(t) for t in entry.metadata["answer"])
            assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    task = DynamicLotSizingPlan()
    entry = task.generate_entry()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("   ", entry) == 0.0
    assert task.score_answer("not a plan", entry) == 0.0


def test_lexicographic_smallest_is_minimal():
    task = DynamicLotSizingPlan()
    entry = task.generate_entry()
    demands = entry.metadata["demands"]
    setup = entry.metadata["setup"]
    holding = entry.metadata["holding"]
    gold = entry.metadata["answer"]
    gold_cost = _plan_cost(gold, demands, setup, holding)
    import itertools

    horizon = len(demands)
    min_cost = None
    min_plan = None
    for r in range(1, horizon + 1):
        for prod in itertools.combinations(range(horizon), r):
            c = _plan_cost(prod, demands, setup, holding)
            if c is None:
                continue
            if min_cost is None or c < min_cost:
                min_cost = c
                min_plan = list(prod)
    assert min_cost == gold_cost
    assert min_plan == gold
    assert _plan_cost(gold, demands, setup, holding) == min_cost


def test_difficulty_changes_config():
    task = DynamicLotSizingPlan()
    c0 = DynamicLotSizingPlan.config_cls()
    c0.set_level(0)
    c6 = DynamicLotSizingPlan.config_cls()
    c6.set_level(6)
    assert c6.horizon > c0.horizon


def test_metadatas_json_serializable():
    import json

    task = DynamicLotSizingPlan()
    entry = task.generate_entry()
    json.dumps(entry.metadata)
