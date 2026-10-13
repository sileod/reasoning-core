from types import SimpleNamespace

import pytest

from reasoning_core.tasks.causal_reasoning import (
    BayesianAssociation,
    BayesianIntervention,
    _to_dict,
    js_divergence,
)


TASKS = (BayesianAssociation, BayesianIntervention)
INVALID_PREDICTIONS = (
    {0: -1.0},
    {0: "nan"},
    {0: "inf"},
    {0: 0.0},
    {},
    {0: 2.0, 1: -1.0},
    {0: "-inf"},
    {0: 1e308, 1: 1e308},
)


@pytest.mark.parametrize("task_type", TASKS)
@pytest.mark.parametrize("prediction", INVALID_PREDICTIONS)
@pytest.mark.parametrize("as_string", (False, True))
def test_invalid_predictions_receive_zero(task_type, prediction, as_string):
    entry = SimpleNamespace(answer="{0: 1.0}")
    answer = repr(prediction) if as_string else prediction

    assert task_type.score_answer(None, answer, entry) == 0


@pytest.mark.parametrize("task_type", TASKS)
def test_valid_predictions_and_state_labels(task_type):
    entry = SimpleNamespace(answer="{0: 1.0, 1: 0.0}")

    assert task_type.task_version == 2
    assert task_type.score_answer(None, {0: 1.0, 1: 0.0}, entry) == 1.0
    assert task_type.score_answer(None, "{'0': 2.0, '1': 0.0}", entry) == 1.0
    entry.answer = "{'heads': 1.0, 'tails': 0.0}"
    assert task_type.score_answer(None, {'heads': 2.0, 'tails': 0.0}, entry) == 1.0
    assert task_type.score_answer(None, "not a distribution", entry) == 0
    assert task_type.score_answer(None, [], entry) == 0


@pytest.mark.parametrize("invalid", INVALID_PREDICTIONS)
def test_direct_divergence_rejects_invalid_operands(invalid):
    valid = {0: 1.0}
    with pytest.raises(ValueError):
        js_divergence(invalid, valid)
    with pytest.raises(ValueError):
        js_divergence(valid, invalid)


def test_direct_divergence_rejects_two_empty_distributions():
    with pytest.raises(ValueError):
        js_divergence({}, {})


@pytest.mark.parametrize("weight", (float("nan"), float("inf"), float("-inf")))
def test_direct_divergence_rejects_nonfinite_float_weights(weight):
    with pytest.raises(ValueError):
        js_divergence({0: weight}, {0: 1.0})


def test_valid_weight_normalization_and_zero_states():
    assert _to_dict({0: 2.0, 1: 0.0}) == {0: 1.0, 1: 0.0}
    assert js_divergence({0: 2.0, 1: 0.0}, {0: 1.0, 1: 0.0}) == 0.0
