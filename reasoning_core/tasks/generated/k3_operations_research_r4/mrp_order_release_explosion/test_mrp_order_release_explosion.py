import json
import random

import pytest

from reasoning_core.tasks.generated.k3_operations_research_r4.mrp_order_release_explosion.mrp_order_release_explosion import (
    MrpOrderReleaseExplosion,
    MrpReleaseConfig,
    solve_mrp,
    verify_plan,
)


def make_instance():
    task = MrpOrderReleaseExplosion()
    task.config.set_level(3)
    entry = task.generate_entry()
    return dict(entry.metadata), entry.answer


def test_generation_smoke():
    task = MrpOrderReleaseExplosion()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_entry()
        assert isinstance(entry.answer, str)
        assert entry.answer.strip().isdigit()
        assert task.score_answer(entry.answer, entry) == 1
        assert 1 <= int(entry.answer) <= entry.metadata["horizon"]


def test_answer_is_first_planned_receipt_period():
    m, ans = make_instance()
    planned, first_shortage = solve_mrp(m)
    assert planned
    assert min(r + m["lead"][i] for r, i, q in planned) == int(ans)
    verify_plan(m, planned, first_shortage)


def test_levels_json_roundtrip_and_prompt():
    task = MrpOrderReleaseExplosion()
    for level in range(7):
        task.config.set_level(level)
        answers = set()
        for _ in range(8):
            entry = task.generate_entry()
            mm = json.loads(json.dumps(dict(entry.metadata)))
            planned, first_shortage = solve_mrp(mm)
            verify_plan(mm, planned, first_shortage)
            assert min(r + mm["lead"][i] for r, i, q in planned) == int(entry.answer)
            prompt = task.render_prompt(mm)
            assert prompt == task.render_prompt(entry.metadata)
            assert len(task.tokenizer.encode(prompt)) < 2048
            assert task.score_answer(entry.answer, entry) == 1
            answers.add(entry.answer)
        assert len(answers) > 1


def test_scoring_uses_no_self_and_exact_match():
    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)

    task = MrpOrderReleaseExplosion()
    entry = task.generate_entry()
    score = MrpOrderReleaseExplosion.score_answer
    assert score(NoAttributes(), entry.answer, entry) == 1
    wrong_answers = ["", "junk", None, "0", str(int(entry.answer) + 1)]
    for wrong in wrong_answers:
        assert score(NoAttributes(), wrong, entry) == 0


def test_fixed_seed_reproduces_without_generator_reseeding():
    state = random.getstate()
    try:
        task = MrpOrderReleaseExplosion()
        first = task.generate_entry()
        after = random.getstate()
        random.setstate(state)
        second = task.generate_entry()
        assert dict(first.metadata) == dict(second.metadata)
        assert first.answer == second.answer
        assert after == random.getstate()
        assert state != after
    finally:
        random.setstate(state)


def test_difficulty_reset_is_not_incremental():
    config = MrpReleaseConfig()
    config.set_level(6)
    high = config.to_dict()
    config.set_level(0)
    assert config.layers == 2
    config.set_level(6)
    assert config.to_dict() == high


def test_answer_domain_positive_valid():
    task = MrpOrderReleaseExplosion()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_entry()
            val = int(entry.answer)
            assert val == int(val) and val >= 1
            assert val <= entry.metadata["horizon"]


def test_gold_answer_backs_into_definition():
    task = MrpOrderReleaseExplosion()
    for _ in range(15):
        entry = task.generate_entry()
        m = dict(entry.metadata)
        planned, first_shortage = solve_mrp(m)
        answer = int(entry.answer)
        assert min(t for t in first_shortage.values() if t is not None) == answer
        # answer is a real receipt period, never a pure release-only artefact
        receipt_periods = [r + m["lead"][i] for r, i, q in planned]
        assert answer in receipt_periods
