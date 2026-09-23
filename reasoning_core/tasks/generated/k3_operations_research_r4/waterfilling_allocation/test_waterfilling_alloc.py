import ast

from reasoning_core.tasks.generated.k3_operations_research_r4.maxmin_waterfilling_allocation.waterfilling_alloc import (
    WaterfillingAllocation,
    waterfill_allocation,
)


def test_gold_roundtrip_all_levels():
    task = WaterfillingAllocation()
    for level in range(7):
        task.config.set_level(level)
        seen = set()
        for _ in range(50):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.answer)
        assert len(seen) > 1


def test_allocation_respects_claims_and_supply():
    task = WaterfillingAllocation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(50):
            ex = task.generate_example()
            claims = ex.metadata["claims"]
            supply = ex.metadata["supply"]
            alloc = ast.literal_eval(ex.answer)
            assert len(alloc) == len(claims)
            assert sum(alloc) <= supply
            for a, c in zip(alloc, claims):
                assert 0 <= a <= c


def test_maxmin_optimality():
    task = WaterfillingAllocation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(50):
            ex = task.generate_example()
            claims = ex.metadata["claims"]
            supply = ex.metadata["supply"]
            alloc = ast.literal_eval(ex.answer)
            n = len(claims)
            # waterfill always consumes the whole supply when claims exceed it;
            # gold alloc[i] must equal min(claims[i], L) for one uniform level L,
            # saturated claims at cap and unsaturated all at L.
            unsat = [alloc[i] for i in range(n) if alloc[i] < claims[i]]
            if unsat:
                L = unsat[0]
                assert all(abs(a - L) < 1e-9 for a in unsat), (claims, supply, alloc)
                for i in range(n):
                    assert abs(alloc[i] - min(claims[i], L)) < 1e-9


def test_uses_full_supply_when_scarce():
    task = WaterfillingAllocation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(50):
            ex = task.generate_example()
            claims = ex.metadata["claims"]
            supply = ex.metadata["supply"]
            if sum(claims) > supply:
                alloc = ast.literal_eval(ex.answer)
                assert sum(alloc) == supply

