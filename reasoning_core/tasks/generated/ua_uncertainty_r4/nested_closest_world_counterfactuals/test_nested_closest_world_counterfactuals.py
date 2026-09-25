import random
import pytest

from reasoning_core.tasks.generated.ua_uncertainty_r4.nested_closest_world_counterfactuals.nested_closest_world_counterfactuals import (
    NestedClosestWorldCounterfactuals,
    NestedCounterfactualConfig,
    closest_world,
    evaluate_answer,
)


def test_generate_and_score_all_levels():
    random.seed(1337)
    task = NestedClosestWorldCounterfactuals()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(40):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert ex.answer in ("yes", "no")
            assert "token" not in ex.answer


def test_junk_scores_zero():
    random.seed(99)
    task = NestedClosestWorldCounterfactuals()
    ex = task.generate_example()
    assert task.score_answer("maybe", ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("Yes indeed", ex) == 0.0


def test_closest_world_unique_and_tie_break():
    worlds = [[0, 0], [0, 1], [1, 0]]
    weights = [1, 1]
    c = closest_world(0, {0: True}, worlds, weights)
    assert c == 2


def test_evaluate_move_and_impossible():
    worlds = [[1, 1], [0, 1], [1, 0]]
    weights = [1, 1]
    clauses = [{"modal": "would", "lits": {0: False, 1: True}}]
    ans, truth = evaluate_answer(worlds, weights, clauses, 1)
    assert (ans, truth) == ("yes", True)


def test_levels_change_config():
    cfg = NestedCounterfactualConfig()
    base = cfg.to_dict()
    cfg.set_level(5)
    assert cfg.num_worlds != base["num_worlds"]
    assert cfg.depth != base["depth"]
