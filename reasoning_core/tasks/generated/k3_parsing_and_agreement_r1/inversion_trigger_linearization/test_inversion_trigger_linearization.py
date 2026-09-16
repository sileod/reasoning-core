import json

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.inversion_trigger_linearization.inversion_trigger_linearization import (
    InversionTriggerLinearization,
)


def test_diff_difficulty_changes_config():
    task = InversionTriggerLinearization()
    task.config.set_level(0)
    base = (task.config.dense, task.config.heavy)
    task.config.set_level(6)
    hi = (task.config.dense, task.config.heavy)
    assert hi != base


def test_metadata_json_serializable():
    task = InversionTriggerLinearization()
    for _ in range(20):
        entry = task.generate_example()
        json.dumps(entry.metadata)



def test_answer_is_base_svo():
    task = InversionTriggerLinearization()
    for _ in range(50):
        entry = task.generate_example()
        answer = entry.answer
        expected = "{0} {1} {2}.".format(
            entry.metadata["subject"],
            entry.metadata["verb"],
            entry.metadata["object"],
        )
        assert answer == expected
        assert "does" not in answer  # no auxiliary in the answer


def test_topicalized_has_inversion():
    task = InversionTriggerLinearization()
    for _ in range(50):
        entry = task.generate_example()
        assert "Only" in entry.metadata["topicalized"]
        assert "does" in entry.metadata["topicalized"]


def test_score_roundtrip():
    task = InversionTriggerLinearization()
    for _ in range(20):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("garbage", entry) == 0.0

