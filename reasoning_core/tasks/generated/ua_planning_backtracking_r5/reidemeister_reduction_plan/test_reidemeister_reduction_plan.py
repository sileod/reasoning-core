import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from dataclasses import asdict

from reasoning_core.template import Task

from reidemeister_reduction_plan import (
    ReidemeisterConfig,
    ReidemeisterReductionPlan,
    _bar,
    _canon,
    _min_reduce,
)


def test_meta_present():
    from reidemeister_reduction_plan import TASK_META
    assert TASK_META['hypothesis'] == 'P005'
    assert TASK_META['parent_source_id'] is None


def test_design_choice_present():
    assert 'random Reidemeister moves' in ReidemeisterReductionPlan.design_choice


def test_generate_all_levels():
    task = ReidemeisterReductionPlan()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(5):
            e = task.generate_example()
            assert e.answer in ('yes', 'no')


def test_answer_matches_budget():
    task = ReidemeisterReductionPlan()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(25):
            e = task.generate_example()
            m = e.metadata['minimum_moves']
            b = e.metadata['budget']
            expected = 'yes' if m <= b else 'no'
            assert e.answer == expected


def test_balanced_labels():
    task = ReidemeisterReductionPlan()
    task.config.set_level(2)
    counts = {'yes': 0, 'no': 0}
    for _ in range(60):
        e = task.generate_example()
        counts[e.answer] += 1
    assert counts['yes'] >= 15
    assert counts['no'] >= 15


def test_gold_scores_one():
    task = ReidemeisterReductionPlan()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    task = ReidemeisterReductionPlan()
    task.config.set_level(0)
    e = task.generate_example()
    assert task.score_answer('', e) == 0.0
    assert task.score_answer('maybe', e) == 0.0
    assert task.score_answer('YES!', e) == 0.0


def test_difficulty_increases_config():
    conf = ReidemeisterConfig()
    conf.set_level(0)
    i0 = conf.insertions
    conf.set_level(6)
    assert conf.insertions > i0


def test_metadata_json_roundtrip():
    task = ReidemeisterReductionPlan()
    task.config.set_level(2)
    e = task.generate_example()
    json.dumps(dict(e.metadata))


def test_bar_involution():
    for a in ('A', 'B', 'C', 'Ab', 'Bb', 'Cb'):
        assert _bar(_bar(a)) == a


def test_min_reduce_adds_two_per_move():
    task = ReidemeisterReductionPlan()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_example()
            c = _min_reduce(list(e.metadata['word']))
            assert c == e.metadata['minimum_moves']
