import random

from reasoning_core.tasks.generated.ua_formal_logic_r4.density_window_rebalancing.density_window_rebalancing import (
    DensityWindowRebalancing,
    _min_moves,
    _bounds,
)


def test_generate_and_score():
    random.seed(12345)
    task = DensityWindowRebalancing()
    entry = task.generate_example()
    meta = dict(entry.metadata)
    assert 0 <= int(entry.answer) <= sum(meta["records"]) + 1
    assert task.score_answer(entry.answer, entry) == 1.0


def test_balance_levels():
    random.seed(99)
    task = DensityWindowRebalancing()
    answers = set()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            answers.add(task.generate_example().answer)
    assert len(answers) >= 2


def test_garbage_not_scored():
    random.seed(7)
    task = DensityWindowRebalancing()
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("junk", entry) < 1.0
    assert task.score_answer(None, entry) < 1.0
    assert task.score_answer(str(int(entry.answer) + 1), entry) < 1.0


def test_bounds_consistency():
    for k in range(2, 9):
        for a in (0.2, 0.3, 0.5, 0.66, 0.75):
            for b in (0.4, 0.6, 0.8, 1.0):
                if b <= a:
                    continue
                lo, hi = _bounds(k, a, b)
                assert 0 <= lo <= k
                assert 0 <= hi <= k
                if lo <= hi:
                    assert lo == ceil(a * k)
                    assert hi == floor(b * k)
                else:
                    assert hi < lo


def test_fully_saturated_rebalance():
    random.seed(5)
    for _ in range(50):
        n = random.randint(10, 20)
        k = random.randint(3, 5)
        if n < k + 2:
            continue
        lo = random.randint(1, k - 1)
        hi = random.randint(lo, k)
        a = (lo - 0.0) / k
        b = (hi + 0.0) / k
        if b > 1.0:
            continue
        bits = [1 if random.random() < 0.5 else 0 for _ in range(n)]
        moves = _min_moves(bits, k, min(a, max(lo / k, 0.0)), min(b, 1.0))
        if moves is not None:
            assert moves >= 0


from math import ceil as _c, floor as _f


def ceil(x):
    return _c(x - 1e-9)


def floor(x):
    return _f(x + 1e-9)
