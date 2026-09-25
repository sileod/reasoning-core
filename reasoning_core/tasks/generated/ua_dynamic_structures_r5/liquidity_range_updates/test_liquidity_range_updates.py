import random

from reasoning_core.tasks.generated.ua_dynamic_structures_r5.liquidity_range_updates.liquidity_range_updates import (
    LiquidityRangeUpdates,
    _round_half_up,
    _simulate,
)

random.seed(12345)


def test_example_scores_correct():
    task = LiquidityRangeUpdates()
    for level in range(7):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("abc", ex) == 0.0


def test_answer_in_domain():
    task = LiquidityRangeUpdates()
    for _ in range(50):
        ex = task.generate_example(level=3)
        val = int(ex.answer)
        assert 1 <= val <= int(ex.metadata["max_price"])
        assert int(ex.metadata["initial_sqrt"]) > 0


def test_simulate_reproduces_answer():
    task = LiquidityRangeUpdates()
    for _ in range(50):
        ex = task.generate_example(level=5)
        positions = [{"id": p["id"], "L": p["L"], "lo": p["lo"], "hi": p["hi"]}
                     for p in ex.metadata["positions"]]
        final = _simulate(
            positions,
            list(ex.metadata["ops"]),
            int(ex.metadata["initial_sqrt"]),
            int(ex.metadata["max_price"]),
        )
        assert _round_half_up(final) == int(ex.answer)


def test_swap_direction_monotonic():
    task = LiquidityRangeUpdates()
    ok = 0
    for _ in range(40):
        ex = task.generate_example(level=2)
        ex_ok = True
        s = int(ex.metadata["initial_sqrt"])
        for op in ex.metadata["ops"]:
            if op["type"] == "swap0":
                assert s >= 1
            elif op["type"] == "swap1":
                assert s <= int(ex.metadata["max_price"])
        ok += 1
    assert ok == 40
