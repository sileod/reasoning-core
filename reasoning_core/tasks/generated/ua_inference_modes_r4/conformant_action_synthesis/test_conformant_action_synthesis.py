import json

import pytest

from reasoning_core.tasks.generated.ua_inference_modes_r4.conformant_action_synthesis.conformant_action_synthesis import (
    ConformantActionSynthesis,
    ConformantActionConfig,
    _find_plan,
)

TASK = ConformantActionSynthesis()


def test_generate_and_score():
    entry = TASK.generate_example()
    assert entry.prompt
    assert TASK.score_answer(entry.answer, entry) == 1.0
    assert TASK.score_answer("", entry) < 1.0
    assert TASK.score_answer("junk", entry) < 1.0


def test_metadata_json_serializable():
    entry = TASK.generate_example()
    json.dumps(dict(entry.metadata))


def test_answer_format():
    for _ in range(20):
        entry = TASK.generate_example()
        answer = entry.answer
        names = {a['name'] for a in entry.metadata['actions']}
        assert answer, "plan must be non-empty"
        for tok in answer.split(';'):
            assert tok in names


def test_plan_is_valid_and_shortest():
    cfg = ConformantActionConfig()
    for _ in range(30):
        entry = TASK.generate_example()
        meta = entry.metadata
        plan = entry.answer.split(';')
        goal = frozenset(meta['goal'])
        for name in plan:
            assert name in {a['name'] for a in meta['actions']}
        replan = _find_plan(meta['actions'], meta['initials'], meta['budget'], goal)
        assert tuple(plan) == replan


def test_difficulty_changes():
    t = ConformantActionSynthesis()
    t.config.set_level(0)
    c0 = t.config.to_dict()
    t.config.set_level(6)
    c6 = t.config.to_dict()
    assert c0 != c6


def test_levels_all_generate():
    t = ConformantActionSynthesis()
    for level in (0, 2, 3, 5, 6):
        t.config.set_level(level)
        entry = t.generate_example()
        assert entry.answer
        assert t.score_answer(entry.answer, entry) == 1.0


def test_budget_respected():
    t = ConformantActionSynthesis()
    t.config.set_level(6)
    for _ in range(50):
        entry = t.generate_example()
        meta = entry.metadata
        plan = entry.answer.split(';')
        total = sum(a['cost'] for a in meta['actions'] if a['name'] in plan)
        assert total <= meta['budget']
