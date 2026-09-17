import itertools
import json
import random
from unittest.mock import patch

import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.criterion_shift_detection.criterion_shift_detection import (
    CriterionShiftConfig,
    CriterionShiftDetection,
    _simulate,
    _verify,
)


def oracle(c0, delta, trials):
    thresholds, responses = [], []
    hits = false_alarms = misses = 0
    for truth, strength in trials:
        threshold = c0 + delta * (false_alarms - misses)
        thresholds.append(threshold)
        response = "yes" if strength >= threshold else "no"
        responses.append(response)
        hits += truth == "signal" and response == "yes"
        false_alarms += truth == "noise" and response == "yes"
        misses += truth == "signal" and response == "no"
    return responses, thresholds, hits, false_alarms


@pytest.mark.parametrize("level", [0, 0.5, 2, 3, 5, 6])
def test_generated_answers_and_render_roundtrip(level):
    random.seed(1000 + level)
    task = CriterionShiftDetection()
    task.config.set_level(level)
    seen = set()
    for _ in range(100):
        entry = task.generate_entry()
        metadata = json.loads(json.dumps(entry.metadata))
        expected = oracle(metadata["starting_criterion"], metadata["step"], metadata["trials"])
        assert expected == (metadata["responses"], metadata["criteria"], metadata["hits"], metadata["false_alarms"])
        mode = metadata["mode"]
        seen.add(mode)
        if mode == "responses":
            assert entry.answer == " ".join(expected[0])
        elif mode == "totals":
            assert entry.answer == f"H={expected[2]} FA={expected[3]}"
        else:
            assert entry.answer == str(expected[1][metadata["queried_trial"] - 1])
        assert task.render_prompt(entry.metadata) == task.render_prompt(metadata)
        assert task.score_answer(entry.answer, entry) == 1.0
        for junk in ("", "junk", "nan", "inf", "[]", None, "1.0000000001", "9" * 10000):
            assert task.score_answer(junk, entry) == 0.0
    assert seen == {"responses", "totals", "criterion"}


def test_exhaustive_short_sequences():
    rows = list(itertools.product(("signal", "noise"), (-1, 0, 1)))
    for trials in itertools.product(rows, repeat=4):
        for c0, delta in itertools.product((-1, 0, 1), (1, 2)):
            result = _simulate(c0, delta, trials)
            assert result == oracle(c0, delta, trials)
            _verify(c0, delta, trials, *result)


def test_all_four_outcomes_and_equality():
    trials = [("signal", 0), ("noise", -1), ("noise", 0), ("signal", 0), ("signal", 0)]
    result = _simulate(0, 2, trials)
    assert result == (["yes", "no", "yes", "no", "yes"], [0, 0, 0, 2, 0], 2, 1)
    _verify(0, 2, trials, *result)
    with pytest.raises(AssertionError):
        _verify(0, 2, trials, result[0], [0, 0, 0, 0, 0], 2, 1)
    with pytest.raises(AssertionError):
        _verify(0, 2, trials, result[0], result[1], 3, 1)


@pytest.mark.parametrize("level", [0, 3, 6])
def test_shift_dependencies_and_parameter_variety(level):
    random.seed(23 + level)
    task = CriterionShiftDetection()
    task.config.set_level(level)
    starts, steps, answers = set(), set(), set()
    for _ in range(150):
        entry = task.generate_entry()
        m = entry.metadata
        starts.add(m["starting_criterion"])
        steps.add(m["step"])
        answers.add(entry.answer)
        prefix = list(zip(m["trials"][:m["queried_trial"] - 1], m["responses"]))
        assert any(t == "signal" and r == "no" for (t, _), r in prefix)
        assert any(t == "noise" and r == "yes" for (t, _), r in prefix)
        assert any((x >= m["starting_criterion"]) != (r == "yes")
                   for (_, x), r in zip(m["trials"], m["responses"]))
    assert len(starts) >= 15
    assert len(steps) == 5
    assert len(answers) > 25


def test_scorer_without_self_and_near_misses():
    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)

    examples = [
        (Entry(metadata={"mode": "responses"}, answer="yes no yes"), "yes yes yes"),
        (Entry(metadata={"mode": "totals", "hits": 3, "false_alarms": 2}, answer="H=3 FA=2"), "H=2 FA=3"),
        (Entry(metadata={"mode": "criterion"}, answer="-4"), "-3"),
    ]
    for entry, wrong in examples:
        assert CriterionShiftDetection.score_answer(NoAttributes(), entry.answer, entry) == 1.0
        assert CriterionShiftDetection.score_answer(NoAttributes(), wrong, entry) == 0.0


def test_seed_reproducibility_and_no_reseeding():
    task = CriterionShiftDetection()
    random.seed(71)
    with patch.object(random, "seed", side_effect=AssertionError("reseeded")):
        first = [task.generate_entry() for _ in range(20)]
    random.seed(71)
    second = [task.generate_entry() for _ in range(20)]
    assert [(e.metadata, e.answer) for e in first] == [(e.metadata, e.answer) for e in second]


def test_difficulty_reset_and_contract():
    config = CriterionShiftConfig()
    config.set_level(6)
    assert config.n_trials == 30
    config.set_level(0)
    assert config.n_trials == 6
    CriterionShiftDetection().validate()
