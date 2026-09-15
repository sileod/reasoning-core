import random

from reasoning_core.tasks.generated.k3_planning_backtracking_r1.pickup_delivery_route_search.pickup_delivery_route_search import (
    PickupDeliveryRouteSearch,
)


def test_generate_and_score():
    task = PickupDeliveryRouteSearch()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_garbage_does_not_score():
    task = PickupDeliveryRouteSearch()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("junk answer here", x) == 0.0
    assert task.score_answer(123, x) == 0.0


def test_difficulty_changes_config():
    task = PickupDeliveryRouteSearch()
    task.config.set_level(0)
    c0 = (task.config.num_jobs, task.config.grid_size, task.config.capacity)
    task.config.set_level(6)
    c6 = (task.config.num_jobs, task.config.grid_size, task.config.capacity)
    assert c0 != c6
    assert task.config.num_jobs > 3


def test_route_is_valid_structure():
    task = PickupDeliveryRouteSearch()
    x = task.generate_example()
    n = len(x.metadata["jobs"])
    answer = x.answer
    # every job pick and deliver appears, in that order
    for j in range(n):
        assert f"{j}P" in answer
        assert f"{j}D" in answer
        assert answer.index(f"{j}P") < answer.index(f"{j}D")


def test_route_respects_capacity_and_optimal():
    from reasoning_core.tasks.generated.k3_planning_backtracking_r1.pickup_delivery_route_search.pickup_delivery_route_search import (
        manhattan,
    )

    task = PickupDeliveryRouteSearch()
    for level in (0, 1, 2):
        task.config.set_level(level)
        n = task.config.num_jobs
        cap = task.config.capacity
        for _ in range(30):
            x = task.generate_example()
            jobs = x.metadata["jobs"]
            answer = x.answer
            cell_of = [c for job in jobs for c in job]
            # parse answer events in order, tracking load and enforcement
            pos = (0, 0)
            load = 0
            cost = 0
            picked = set()
            delivered = set()
            i = 0
            while i < len(answer):
                j = int(answer[i])
                i += 1
                ev = answer[i]
                i += 1
                if ev == "P":
                    c = jobs[j][0]
                    assert load < cap, "capacity violated"
                    assert j not in picked
                    picked.add(j)
                    load += 1
                else:
                    c = jobs[j][1]
                    assert j in picked and j not in delivered
                    delivered.add(j)
                    load -= 1
                cost += manhattan(pos, c)
                pos = c
            assert delivered == set(range(n))
            # cost equals recorded optimal cost
            assert cost == x.metadata["cost"]

