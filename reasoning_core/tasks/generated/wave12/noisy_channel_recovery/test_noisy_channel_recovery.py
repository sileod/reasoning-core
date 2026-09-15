import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.wave12.noisy_channel_recovery.noisy_channel_recovery import (
    NoisyChannelRecovery,
)


def test_gold_scores_one():
    task = NoisyChannelRecovery()
    task.config.set_level(3)
    for _ in range(20):
        entry = task.generate_entry()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_set_matches_intended():
    task = NoisyChannelRecovery()
    task.config.set_level(2)
    for _ in range(20):
        entry = task.generate_entry()
        expected = sorted(set(entry.metadata["intended"]))
        parts = [p.strip() for p in entry.answer.split(",")]
        assert sorted(parts) == expected


def test_junk_scores_zero():
    task = NoisyChannelRecovery()
    task.config.set_level(0)
    entry = task.generate_entry()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) < 1.0


def test_difficulty_changes():
    task = NoisyChannelRecovery()
    task.config.set_level(0)
    l0 = task.config.length
    task.config.set_level(5)
    l5 = task.config.length
    assert l5 > l0


def test_metadata_json_serializable():
    import json

    task = NoisyChannelRecovery()
    task.config.set_level(4)
    entry = task.generate_entry()
    json.dumps(entry.metadata)


def test_constant_answer_not_produced():
    random.seed(960070481)
    task = NoisyChannelRecovery()
    task.config.set_level(0)
    answers = set()
    for _ in range(30):
        entry = task.generate_entry()
        answers.add(entry.answer)
    assert len(answers) >= 2
