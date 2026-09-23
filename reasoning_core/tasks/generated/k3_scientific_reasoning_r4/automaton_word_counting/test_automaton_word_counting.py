import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from automaton_word_counting import AutomatonWordCounting


def test_generate_and_score():
    task = AutomatonWordCounting()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_difficulty_changes_config():
    task = AutomatonWordCounting()
    task.config.set_level(0)
    l0 = (task.config.n, task.config.length, task.config.product, task.config.use_eps)
    task.config.set_level(5)
    l5 = (task.config.n, task.config.length, task.config.product, task.config.use_eps)
    assert l0 != l5


def test_levels_generate():
    for level in range(7):
        task = AutomatonWordCounting()
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_both_answer_modes():
    task = AutomatonWordCounting()
    task.config.range_total = True
    x = task.generate_example()
    assert task.config.range_total is True
    assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    task = AutomatonWordCounting()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("not a number", x) == 0.0


def test_label_spread():
    task = AutomatonWordCounting()
    answers = []
    for _ in range(80):
        x = task.generate_example()
        answers.append(int(x.answer))
    distinct = len(set(answers))
    assert distinct >= 5, "answers too concentrated: %r" % set(answers)
    mode = max(set(answers), key=answers.count)
    assert answers.count(mode) < 60, "single answer dominates"


def test_metadata_json_serializable():
    import json

    task = AutomatonWordCounting()
    x = task.generate_example()
    json.dumps(x.metadata)
