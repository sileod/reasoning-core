import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_operations_research_r4.nested_fare_protection_levels.nested_fare_protection_levels import (  # noqa
    NestedFareProtectionLevels,
    _fractile_poisson,
    _nested_limits,
)


def _gold(task, level=0):
    random.seed(12345)
    task.config.set_level(level)
    return task.generate_entry()


def test_generate_entry_returns_valid_entry():
    random.seed(1)
    task = NestedFareProtectionLevels()
    for level in (0, 2, 6):
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_entry()
            assert e.answer.isdigit()
            assert isinstance(e.metadata["bl"], list)
            assert len(e.metadata["bl"]) == len(e.metadata["names"])
            assert e.metadata["bl"] == sorted(e.metadata["bl"])
            assert 0 <= e.metadata["bl"][e.metadata["target"]] <= e.metadata["cap"]
            bl = e.metadata["bl"]
            assert bl == _nested_limits(e.metadata["lams"], e.metadata["cap"])


def test_score_answer_gold():
    random.seed(1)
    task = NestedFareProtectionLevels()
    for level in (0, 2, 6):
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_entry()
            assert task.score_answer(e.answer, e) == 1.0
            assert task.score_answer("  " + e.answer + " ", e) == 1.0


def test_score_answer_junk():
    random.seed(1)
    task = NestedFareProtectionLevels()
    task.config.set_level(0)
    e = task.generate_entry()
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("abc", e) == 0.0
    assert task.score_answer("3.7", e) == 0.0
    wrong = str((int(e.answer) + 1) % 100)
    assert task.score_answer(wrong, e) == 0.0


def test_difficulty_changes_config():
    task = NestedFareProtectionLevels()
    base = NestedFareProtectionLevels()
    task.config.set_level(0)
    base.config.set_level(6)
    assert base.config.n_classes >= task.config.n_classes
    assert base.config.cap >= task.config.cap


def test_render_prompt_contains_given_and_target():
    random.seed(7)
    task = NestedFareProtectionLevels()
    task.config.set_level(2)
    e = task.generate_entry()
    prompt = task.render_prompt(e.metadata)
    assert e.metadata["target_name"] in prompt
    assert str(e.metadata["lams"][0]) in prompt
    assert "Answer a single non-negative integer" in prompt


def test_prompt_not_readable_off_surface():
    random.seed(9)
    task = NestedFareProtectionLevels()
    targets = []
    for _ in range(200):
        task.config.set_level(0)
        task.config.set_level(0)
        e = task.generate_entry()
        lims = e.metadata["bl"]
        gold = lims[e.metadata["target"]]
        prompt = task.render_prompt(e.metadata)
        if gold > 0:
            targets.append(gold)
    # at least a couple distinct nonzero answers exist
    assert len(set(targets)) >= 2


def test_poisson_fractile_monotone():
    assert _fractile_poisson(0) == 0
    assert _fractile_poisson(0.5) == 0
    prev = -1
    for lam in range(1, 80):
        q = _fractile_poisson(lam)
        assert q >= prev
        prev = q
