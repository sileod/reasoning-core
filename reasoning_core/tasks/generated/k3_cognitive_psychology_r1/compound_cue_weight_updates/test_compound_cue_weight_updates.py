import itertools
import json
import random
from fractions import Fraction
from unittest.mock import patch

import pytest

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.compound_cue_weight_updates.compound_cue_weight_updates import (
    CompoundCueWeightUpdates,
    _run_rescorla_wagner,
    _verify_weights,
)


@pytest.fixture(autouse=True)
def fixed_random_state():
    state = random.getstate()
    random.seed(3020341981)
    yield
    random.setstate(state)


@pytest.mark.parametrize("level", range(7))
def test_generated_gold_and_balance(level):
    task = CompoundCueWeightUpdates()
    task.config.set_level(level)
    answers = []
    prompts = set()
    modes = set()
    for _ in range(100):
        entry = task.generate_entry()
        restored = json.loads(json.dumps(entry.metadata))
        weights = _verify_weights(restored["phases"], restored["rates"])
        other = "B" if entry.answer == "A" else "A"
        assert weights[entry.answer] > weights[other]
        assert {cue: str(value) for cue, value in weights.items()} == restored["weights_final"]
        assert task.score_answer(entry.answer, entry) == 1
        assert task.score_answer(other, entry) == 0
        assert task.render_prompt(restored) == task.render_prompt(entry.metadata)
        answers.append(entry.answer)
        prompts.add(task.render_prompt(restored))
        modes.add(restored["mode"])
    assert 30 <= answers.count("A") <= 70
    assert len(prompts) >= 90
    assert modes == {"acquisition", "blocking", "inhibition", "extinction"}


def test_known_learning_cases():
    rates = {"A": 3, "B": 3}
    acquisition = _run_rescorla_wagner([["A", 1, 2]], rates)
    assert acquisition == {"A": Fraction(7, 16), "B": 0}
    blocking = _run_rescorla_wagner([["A", 1, 2], ["AB", 1, 1]], rates)
    assert blocking == {"A": Fraction(37, 64), "B": Fraction(9, 64)}
    naive = _run_rescorla_wagner([["AB", 1, 1]], rates)
    assert blocking["B"] < naive["B"]
    inhibition = _run_rescorla_wagner([["A", 1, 2], ["AB", 0, 1]], rates)
    assert inhibition == {"A": Fraction(21, 64), "B": Fraction(-7, 64)}
    extinction = _run_rescorla_wagner([["A", 1, 2], ["A", 0, 1]], rates)
    assert extinction == {"A": Fraction(21, 64), "B": 0}


def test_simultaneous_updates_and_absent_cues():
    rates = {"A": 2, "B": 4, "C": 3}
    weights = _run_rescorla_wagner([["AB", 1, 1]], rates)
    assert weights == {"A": Fraction(1, 6), "B": Fraction(1, 3), "C": 0}
    assert _run_rescorla_wagner([["BA", 1, 1]], rates) == weights


def test_trial_order_changes_response():
    rates = {"A": 3, "B": 3}
    first = _run_rescorla_wagner([["A", 1, 1], ["AB", 0, 1]], rates)
    second = _run_rescorla_wagner([["AB", 0, 1], ["A", 1, 1]], rates)
    assert first != second


def test_exhaustive_short_schedules():
    kinds = [(cues, outcome, 1) for cues in ("A", "B", "AB") for outcome in (0, 1)]
    for schedule in itertools.product(kinds, repeat=3):
        for rates in ({"A": 2, "B": 4}, {"A": 3, "B": 3}):
            assert _run_rescorla_wagner(schedule, rates) == _verify_weights(schedule, rates)


def test_scoring_without_self_access():
    class NoAccess:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = CompoundCueWeightUpdates().generate_entry()
    scorer = CompoundCueWeightUpdates.score_answer
    assert scorer(NoAccess(), entry.answer, entry) == 1
    assert scorer(NoAccess(), f" {entry.answer}\n", entry) == 1
    for answer in ("", "junk", "AB", "A or B", None, [], 1, entry.answer.lower()):
        assert scorer(NoAccess(), answer, entry) == 0


def test_difficulty_and_reproducibility():
    task = CompoundCueWeightUpdates()
    settings = []
    for level in range(7):
        task.config.set_level(level)
        settings.append((task.config.n_phases, task.config.max_repeats, task.config.n_cues))
    assert all(a <= b for a, b in zip(settings, settings[1:]))
    task.config.set_level(0)
    assert settings[0] == (task.config.n_phases, task.config.max_repeats, task.config.n_cues)
    state = random.getstate()
    first = task.generate_entry()
    random.setstate(state)
    second = task.generate_entry()
    assert first.metadata == second.metadata
    assert first.answer == second.answer


def test_bounded_rejection():
    task = CompoundCueWeightUpdates()
    task.config.max_attempts = 3
    module = CompoundCueWeightUpdates.__module__
    with patch(module + "._random_schedule", return_value=("extinction", [["AB", 0, 1]])) as schedule:
        with pytest.raises(RuntimeError, match="bounded attempts"):
            task.generate_entry()
    assert schedule.call_count == 3


def test_prompt_states_all_rules():
    task = CompoundCueWeightUpdates()
    entry = task.generate_entry()
    prompt = task.render_prompt(entry.metadata)
    for text in ("start at 0", "simultaneously", "Absent cues do not change", "without clipping",
                 "+ means outcome 1", "- means outcome 0", "left to right", "recomputing error",
                 "Before any probe update", "signed weights", "single letter", "for example: A"):
        assert text in prompt
