import random

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.joint_share_information.joint_share_information import JointShareInformation


def test_generate_and_score():
    random.seed(123)
    task = JointShareInformation()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_deterministic_seed():
    random.seed(99)
    t1 = JointShareInformation()
    e1 = t1.generate_entry()
    random.seed(99)
    t2 = JointShareInformation()
    e2 = t2.generate_entry()
    assert e1.answer == e2.answer


def test_metadata_json_serializable():
    import json
    random.seed(7)
    task = JointShareInformation()
    task.config.set_level(4)
    entry = task.generate_example()
    json.dumps(entry.metadata)
    assert entry.answer in ("0", "1", "01", "none", "yes", "no", "recovery", "perfect", "leakage")


def test_config_changes_difficulty():
    task = JointShareInformation()
    task.config.set_level(0)
    l0 = task.render_prompt(task.generate_example().metadata)
    assert len(l0) > 0


def test_all_answer_types_occur():
    random.seed(5)
    task = JointShareInformation()
    seen = set()
    for _ in range(400):
        seen.add(task.generate_entry().answer)
    assert {"yes", "no"} <= seen
    assert {"recovery", "perfect", "leakage"} <= seen
