"""Tests for centering_transition_tracking."""

import json

from reasoning_core.tasks.generated.k3_controlled_nli_r1.centering_transition_tracking import (
    centering_transition_tracking as mod,
)

TASK_CLS = mod.CenteringTransitionTracking
CONFIG_CLS = mod.CenteringTransitionTrackingConfig


def _task(level):
    task = TASK_CLS()
    task.config.set_level(level)
    return task


def test_generate_and_score_all_levels():
    for level in range(7):
        task = _task(level)
        for _ in range(10):
            entry = task.generate_entry()
            labels = entry.answer.split(",")
            assert len(labels) == task.config.n_utterances - 1
            assert all(label in mod.LABELS for label in labels)
            assert task.score_answer(entry.answer, entry) == 1.0
            assert task.score_answer(entry.answer.upper(), entry) == 1.0


def test_score_rejects_wrong_answers():
    task = TASK_CLS()
    entry = task.generate_entry()
    wrong = ",".join("shift" if lb != "shift" else "continue"
                     for lb in entry.answer.split(","))
    assert task.score_answer(wrong, entry) == 0.0
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("continue", entry) == 0.0
    assert task.score_answer("the answer is " + entry.answer, entry) == 0.0


def test_labels_are_varied():
    task = _task(4)
    seen = set()
    for _ in range(200):
        seen.update(task.generate_entry().answer.split(","))
    assert seen == set(mod.LABELS)


def test_backward_center_and_transitions_consistent():
    for level in (0, 3, 6):
        task = _task(level)
        for _ in range(20):
            entry = task.generate_entry()
            cfs = [tuple(cf) for cf in entry.metadata["cf_lists"]]
            labels = mod._transitions(cfs)
            assert ",".join(labels) == entry.answer
            # each utterance text is rendered and non-empty
            for text, cf in zip(entry.metadata["utterances"], cfs):
                assert text.endswith(".")
                assert len(cf) >= 1


def test_metadata_json_serializable():
    task = _task(2)
    entry = task.generate_entry()
    json.dumps(entry.metadata)


def test_difficulty_changes_config():
    cfg = CONFIG_CLS()
    cfg.set_level(0)
    small = (cfg.n_utterances, cfg.pronoun_prob)
    cfg.set_level(6)
    big = (cfg.n_utterances, cfg.pronoun_prob)
    assert big[0] > small[0]
    assert big[1] > small[1]


def test_first_utterance_names_both_entities():
    task = _task(1)
    for _ in range(10):
        entry = task.generate_entry()
        assert len(entry.metadata["cf_lists"][0]) == 2
