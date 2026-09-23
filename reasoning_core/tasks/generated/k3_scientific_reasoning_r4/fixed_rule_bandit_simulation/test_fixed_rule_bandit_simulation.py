import random
from pathlib import Path

import pytest

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.fixed_rule_bandit_simulation.fixed_rule_bandit_simulation import (
    FixedRuleBanditSimulation,
    _simulate,
)


def _task():
    return FixedRuleBanditSimulation()


def test_gold_scores_one():
    task = _task()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1


def test_junk_scores_zero():
    task = _task()
    ex = task.generate_example()
    for bad in ("", " ", "reajrj", "1.5", "-3"):
        assert task.score_answer(bad, ex) < 1


def test_levels_generate_distinct():
    task = _task()
    seen = set()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            seen.add(ex.metadata["least_pulled_count"])
    assert len(seen) > 1


def test_difficulty_changes_config():
    task = _task()
    base = task.config.n_arms
    task.config.set_level(6)
    assert task.config.n_arms > base


def test_answer_is_min_of_pull_counts():
    task = _task()
    for _ in range(20):
        ex = task.generate_example()
        assert int(ex.answer) == min(ex.metadata["pull_counts"])


def test_pull_counts_partition_rounds():
    task = _task()
    for _ in range(20):
        ex = task.generate_example()
        assert sum(ex.metadata["pull_counts"]) == ex.metadata["rounds"]
        assert min(ex.metadata["pull_counts"]) >= 1


def test_simulation_consistency():
    # Every round chooses exactly one arm; counts are consistent.
    for level in (0, 2, 5):
        t = _task()
        t.config.set_level(level)
        cfg = t.config
        rounds = 20
        streams = [[1 if random.random() < 0.5 else 0 for _ in range(rounds)]
                   for _ in range(cfg.n_arms)]
        for policy in ("epsilon", "ucb", "thompson"):
            succ, pull, choices = _simulate(
                cfg.n_arms, rounds, streams, policy, 2, 1.0
            )
            assert len(choices) == rounds
            assert sum(pull) == rounds
            from collections import Counter
            counts = Counter(choices)
            for i in range(cfg.n_arms):
                assert counts[i] == pull[i]
                assert succ[i] == sum(streams[i][:pull[i]])


def test_metadata_json_serializable():
    import json
    task = _task()
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))


def test_balanced_binary_like_variety():
    # No single min-count value should dominate a sample.
    task = _task()
    answers = []
    for _ in range(60):
        answers.append(task.generate_example().answer)
    top = max(set(answers), key=answers.count)
    assert answers.count(top) < 0.5 * len(answers)


def _independent_min_pull(metadata):
    """A from-scratch, spec-only simulation of the same instance."""
    import math as _m
    from scipy.stats import beta as _b
    n = metadata["n_arms"]
    rounds = metadata["rounds"]
    streams = metadata["streams"]
    policy = metadata["policy"]
    step = metadata["explore_step"]
    c = metadata["ucb_c"]
    grid = metadata.get("grid")
    succ = [0] * n
    pull = [0] * n
    for r in range(1, rounds + 1):
        if policy == "epsilon":
            if r % step == 0:
                idx = min(range(n), key=lambda i: (pull[i], i))
            else:
                vals = [(-1e18 if pull[i] == 0 else succ[i] / pull[i]) for i in range(n)]
                idx = min(range(n), key=lambda i: (-vals[i], i))
        elif policy == "ucb":
            vals = [
                (float("inf") if pull[i] == 0
                 else succ[i] / pull[i] + c * _m.sqrt(_m.log(r) / pull[i]))
                for i in range(n)
            ]
            idx = min(range(n), key=lambda i: (-vals[i], i))
        else:
            eps = 1e-9
            vals = []
            for i in range(n):
                u = grid[(i * 7 + r * 13) % len(grid)]
                alpha = 1 + succ[i]
                bt = 1 + (pull[i] - succ[i])
                u = min(max(u, eps), 1.0 - eps)
                vals.append(_b.ppf(u, alpha, bt))
            idx = min(range(n), key=lambda i: (-vals[i], i))
        succ[idx] += streams[idx][pull[idx]]
        pull[idx] += 1
    return min(pull)


def test_independent_simulation_matches_gold():
    task = _task()
    for _ in range(25):
        ex = task.generate_example()
        independent = _independent_min_pull(ex.metadata)
        assert int(ex.answer) == independent
