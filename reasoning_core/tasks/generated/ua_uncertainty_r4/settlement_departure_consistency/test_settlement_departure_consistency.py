"""Focused tests for the SettlementDepartureConsistency task."""
import json
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from reasoning_core.template import Entry, edict
from settlement_departure_consistency import (
    SettlementDepartureConsistency,
    _waterfill,
    _proportional,
)


def _balancing_estimate(task, n=40):
    counts = {}
    for _ in range(n):
        e = task.generate_example()
        counts[e.answer] = counts.get(e.answer, 0) + 1
    return counts


def test_gold_scores_one_every_level():
    task = SettlementDepartureConsistency()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(8):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0, (level, e.answer)


def test_answers_not_all_same_every_level():
    task = SettlementDepartureConsistency()
    for level in (0, 3, 6):
        task.config.set_level(level)
        answers = {task.generate_example().answer for _ in range(40)}
        assert len(answers) >= 2, (level, answers)


def test_none_not_dominant():
    task = SettlementDepartureConsistency()
    for level in (0, 3, 6):
        task.config.set_level(level)
        n = 60
        none = sum(1 for _ in range(n)
                   if task.generate_example().answer == "none")
        assert none < 0.45 * n, (level, none / n)


def test_garbage_not_scored_one():
    task = SettlementDepartureConsistency()
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("garbage output", e) < 1.0
    assert task.score_answer(str(int((1e9))), e) < 1.0


def test_difficulty_changes_config():
    task = SettlementDepartureConsistency()
    task.config.set_level(0)
    lo = task.config.n_max
    task.config.set_level(6)
    hi = task.config.n_max
    assert hi >= lo


def test_reproducible_under_fixed_seed():
    random.seed(7)
    e1 = SettlementDepartureConsistency().generate_example()
    random.seed(7)
    e2 = SettlementDepartureConsistency().generate_example()
    assert e1.answer == e2.answer
    assert e1.metadata["estate"] == e2.metadata["estate"]


def test_answer_varies():
    task = SettlementDepartureConsistency()
    answers = {task.generate_example().answer for _ in range(40)}
    assert len(answers) > 3


def test_metadata_json_serializable():
    task = SettlementDepartureConsistency()
    e = task.generate_example()
    json.dumps({k: v for k, v in e.metadata.items()})
    json.dumps(e.metadata["payload"])


def test_waterfill_priority_saturates_first():
    claims = {"A": 3, "B": 5, "C": 7}
    aw = _waterfill(claims, ["A", "B", "C"], ["A", "B", "C"], 8)
    assert aw == {"A": 3, "B": 5, "C": 0}


def test_proportional_sums_to_estate():
    claims = {"A": 2, "B": 3, "C": 5}
    labels = ["A", "B", "C"]
    aw = _proportional(claims, labels, 10)
    assert aw == {"A": 2, "B": 3, "C": 5}
    assert float(sum(aw.values())) == 10.0


def test_changed_matches_metadata():
    task = SettlementDepartureConsistency()
    e = task.generate_example()
    if e.answer == "none":
        assert e.metadata["changed"] == []
    else:
        assert ", ".join(e.metadata["changed"]) == e.answer
