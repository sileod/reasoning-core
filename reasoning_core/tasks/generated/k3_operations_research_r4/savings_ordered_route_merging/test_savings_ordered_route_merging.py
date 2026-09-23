import random

from reasoning_core.tasks.generated.k3_operations_research_r4.savings_ordered_route_merging.savings_ordered_route_merging import (
    SavingsOrderedRouteMerging,
)


def test_module_loads():
    assert SavingsOrderedRouteMerging is not None
    assert "savings" in SavingsOrderedRouteMerging.summary.lower()


def test_all_levels_generate_and_score():
    random.seed(1234)
    task = SavingsOrderedRouteMerging()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0
            assert task.score_answer("", entry) == 0.0
            assert task.score_answer("garbage", entry) == 0.0


def test_metadata_json_serializable():
    random.seed(99)
    task = SavingsOrderedRouteMerging()
    task.config.set_level(3)
    entry = task.generate_example()
    import json
    json.dumps(entry.metadata)
    assert isinstance(entry.answer, str)


def test_routes_cover_all_customers():
    random.seed(7)
    task = SavingsOrderedRouteMerging()
    for level in range(0, 7):
        task.config.set_level(level)
        entry = task.generate_example()
        routes = entry.metadata["routes"]
        covered = set()
        for r in routes:
            covered.update(r)
        assert covered == set(range(task.config.n_customers))
        for r in routes:
            assert len(set(r)) == len(r)


def test_deterministic_under_seed():
    random.seed(42)
    task = SavingsOrderedRouteMerging()
    task.config.set_level(2)
    e1 = task.generate_example()
    random.seed(42)
    task2 = SavingsOrderedRouteMerging()
    task2.config.set_level(2)
    e2 = task2.generate_example()
    assert e1.answer == e2.answer
