import random

from reasoning_core.tasks.generated.k3_operations_research_r4.penalty_recomputed_transport_assignment.penalty_recomputed_transport_assignment import (
    PenaltyRecomputedTransportAssignment,
    PenaltyRecomputedConfig,
    _vam_allocation,
    _format_alloc,
)


def test_generate_and_score_multiple_levels():
    for level in [0, 1, 2, 5, 6]:
        cfg = PenaltyRecomputedConfig()
        cfg.set_level(level)
        task = PenaltyRecomputedTransportAssignment(config=cfg)
        # several examples
        for _ in range(8):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer("", ex) == 0.0
            assert task.score_answer("junk", ex) == 0.0


def test_allocation_feasible():
    cfg = PenaltyRecomputedConfig()
    task = PenaltyRecomputedTransportAssignment(config=cfg)
    for _ in range(20):
        ex = task.generate_example()
        md = ex.metadata
        alloc = md["alloc"]
        used_s = [0] * len(md["supply"])
        used_d = [0] * len(md["demand"])
        for (i, j, amt) in alloc:
            used_s[i] += amt
            used_d[j] += amt
        assert used_s == md["supply"]
        assert used_d == md["demand"]
        # total cost equals sum over alloc of cost*amount
        tc = sum(md["cost"][i][j] * a for (i, j, a) in alloc)
        assert tc == md["total_cost"]


def test_format_sorted_by_row_then_col():
    alloc = [(2, 0, 5), (0, 1, 3), (0, 0, 1)]
    s = _format_alloc(alloc)
    assert s == "0:0=1;0:1=3;2:0=5"
    # reparse
    entries = [tuple(e) for e in (x.split("=") for x in s.split(";"))]
    assert len(entries) == 3


def test_vam_exhausts_supply_and_demand_small():
    supply = [5, 5]
    demand = [3, 7]
    cost = [[1, 2], [3, 4]]
    alloc, tc = _vam_allocation(supply, demand, cost)
    used_s = [0, 0]
    used_d = [0, 0]
    for (i, j, a) in alloc:
        used_s[i] += a
        used_d[j] += a
    assert used_s == [5, 5]
    assert used_d == [3, 7]


def test_positive_parts_sums_to_total():
    from reasoning_core.tasks.generated.k3_operations_research_r4.penalty_recomputed_transport_assignment.penalty_recomputed_transport_assignment import (
        _positive_parts,
    )
    for total in [10, 20, 110]:
        for k in [1, 2, 3, 7, 15]:
            if k > total:
                continue
            p = _positive_parts(total, k)
            assert len(p) == k
            assert sum(p) == total
            assert all(x >= 1 for x in p)


def test_generation_feasible_all_levels():
    import random
    random.seed(12345)
    for level in range(7):
        cfg = PenaltyRecomputedConfig()
        cfg.set_level(level)
        task = PenaltyRecomputedTransportAssignment(config=cfg)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0

