import random

import pytest

from reasoning_core.tasks.generated.ua_novel_composition_r4.stopped_sample_likelihood_ratio.stopped_sample_likelihood_ratio import (
    StoppedSampleConfig,
    StoppedSampleLikelihoodRatio,
)


def _task_at(level):
    task = StoppedSampleLikelihoodRatio()
    cfg = StoppedSampleConfig()
    cfg.set_level(level)
    task.config = cfg
    return task


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_generates_valid_instance(level):
    task = _task_at(level)
    random.seed(12345 + level)
    entry = task.generate_entry()
    assert isinstance(entry.answer, str)
    int(entry.answer)
    assert task.score_answer(entry.answer, entry) == 1.0


@pytest.mark.parametrize("level", [0, 3, 6])
def test_generated_entry_roundtrip(level):
    task = _task_at(level)
    random.seed(777)
    entry = task.generate_entry()
    prompt = task.render_prompt(entry.metadata)
    assert "log2" in prompt or "likelihood ratio" in prompt
    assert task.score_answer(entry.answer, entry) == 1.0
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("junk", entry) < 1.0


@pytest.mark.parametrize("level", [0, 6])
def test_constraint_no_constant_answer(level):
    task = _task_at(level)
    random.seed(42)
    answers = set()
    for _ in range(60):
        entry = task.generate_entry()
        answers.add(entry.answer)
    assert len(answers) > 1


def test_difficulty_changes_config():
    task = StoppedSampleLikelihoodRatio()
    cfg = StoppedSampleConfig()
    cfg.set_level(0)
    lo = cfg.max_draws
    cfg.set_level(6)
    hi = cfg.max_draws
    assert hi > lo


def test_gold_answer_is_stable_with_recomputation():
    task = _task_at(3)
    random.seed(9)
    entry = task.generate_entry()
    gold = int(round(entry.metadata["mlr_log2"]))
    assert int(entry.answer) == gold


def test_history_rejected_when_impossible_without_replacement():
    task = _task_at(0)
    # a report of more draws than balls must never be accepted for the
    # without-replacement failure-stop case (guarded inside generate_entry)
    random.seed(5)
    for _ in range(200):
        entry = task.generate_entry()
        md = entry.metadata
        if not md["with_replacement"] and not md["stopped_at_success"]:
            if md["stopping"] == "one_success":
                for _w, _N in md["pairs"]:
                    assert md["n"] <= (_N - _w)

