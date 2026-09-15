import random
from fractions import Fraction

from reasoning_core.template import Task

from reasoning_core.tasks.generated.k3_rule_induction_r1.shapley_value_marginal_contributions.shapley_value_marginal_contributions import (
    ShapleyValueMarginalContributions as T,
)


def test_gold_scores_one():
    random.seed(1)
    task = T()
    for _ in range(30):
        entry = task.generate_entry()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    random.seed(2)
    task = T()
    entry = task.generate_entry()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0
    assert task.score_answer("1/0", entry) == 0.0


def test_difficulty_changes_config():
    task = T()
    base = task.config.players
    task.config.set_level(1)
    assert task.config.players > base


def test_answers_are_valid_fractions():
    random.seed(3)
    task = T()
    for _ in range(20):
        entry = task.generate_entry()
        for s in entry.metadata["shapley"]:
            f = Fraction(s)
            assert f.denominator >= 1
