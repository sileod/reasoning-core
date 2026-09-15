"""Tests for the online multiplicative weights task trial."""

import random

from reasoning_core.tasks.generated.k3_relevance_separation_r1.online_multiplicative_weights.online_multiplicative_weights import (
    OnlineMultiplicativeWeights,
)


def _make_task(level):
    task = OnlineMultiplicativeWeights()
    task.config.set_level(level)
    return task


def test_generate_and_score_levels():
    for level in range(7):
        task = _make_task(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("garbage", ex) < 1.0


def test_answer_reproducing_distribution():
    for level in range(7):
        task = _make_task(level)
        ex = task.generate_example()
        n = ex.metadata["n_experts"]
        denom = ex.metadata["denom"]
        nums = [int(p.split("/")[0]) for p in ex.answer.split(",")]
        assert len(nums) == n
        for num, w in zip(nums, ex.metadata["final_weights"]):
            assert abs(num / denom - w) < 1e-6


def test_both_experts_can_lose():
    random.seed(1)
    n = OnlineMultiplicativeWeights().config.n_experts
    seen_losers = set()
    task = _make_task(0)
    for _ in range(100):
        ex = task.generate_example()
        for vec in ex.metadata["losses"]:
            seen_losers.add(vec.index(1))
    assert seen_losers == set(range(n))


def test_answer_nums_positive():
    for level in range(7):
        task = _make_task(level)
        for _ in range(5):
            ex = task.generate_example()
            for num in ex.metadata["answer_nums"]:
                assert num >= 1
