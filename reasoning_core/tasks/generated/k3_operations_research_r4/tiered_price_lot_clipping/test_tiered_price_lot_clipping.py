import math
import random

from reasoning_core.template import Task

from reasoning_core.tasks.generated.k3_operations_research_r4.tiered_price_lot_clipping.tiered_price_lot_clipping import (
    TieredPriceLotClipping,
    _solve,
    _tier_total,
)


def _opt_brute(breaks, prices, D, h, A):
    n = len(prices)
    best = None
    bestq = None
    pmin = min(prices)
    ub = int(math.ceil(math.sqrt(2.0 * A * D / (pmin * (h + 2))))) + 50
    for q in range(1, ub + 1):
        for i in range(n):
            lo = breaks[i]
            hh = breaks[i + 1] if i + 1 < n else None
            if q < lo:
                continue
            if hh is not None and q > hh:
                continue
            val = _tier_total(q, prices[i], D, h, A)
            if best is None or val < best or (abs(val - best) < 1e-9 and q < bestq):
                best = val
                bestq = q
    return best, bestq


def test_solve_matches_bruteforce():
    random.seed(123)
    for _ in range(200):
        n = random.randint(2, 5)
        breaks = [0]
        cur = random.randint(6, 12)
        for _ in range(n - 1):
            cur += random.randint(3, 12)
            breaks.append(cur)
        prices = sorted(random.sample(range(1, 41), n), reverse=True)
        D = random.randint(1000, 3000)
        h = random.randint(2, 8)
        A = random.randint(20, 120)
        best, qopt, cands = _solve(breaks, prices, D, h, A)
        bbest, bqopt = _opt_brute(breaks, prices, D, h, A)
        assert len(set(prices)) == n
        assert qopt == bqopt, (breaks, prices, qopt, bqopt)


def test_prices_strictly_decreasing():
    random.seed(7)
    for _ in range(100):
        n = random.randint(2, 5)
        breaks = [0]
        cur = random.randint(6, 12)
        for _ in range(n - 1):
            cur += random.randint(3, 12)
            breaks.append(cur)
        prices = sorted(random.sample(range(1, 41), n), reverse=True)
        assert all(prices[i] > prices[i + 1] for i in range(n - 1))


def test_levels_wide():
    task = TieredPriceLotClipping()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(10):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert ex.metadata["qopt"] >= 1
            assert ex.metadata["total_cost"] > 0
