from reasoning_core.tasks.generated.ua_latent_structure_reconstruction_r4.sandpile_recurrence_membership.task_sandpile_recurrence_membership import (
    SandpileRecurrenceMembership,
)


def test_gold_scores_1():
    task = SandpileRecurrenceMembership()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(3):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_wrong_answers_score_0():
    task = SandpileRecurrenceMembership()
    task.config.set_level(3)
    entry = task.generate_example()
    expected = entry.answer
    other = "transient" if expected == "recurrent" else "recurrent"
    assert task.score_answer(other, entry) == 0.0
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("maybe", entry) == 0.0


def test_answer_is_recurrent_or_transient():
    task = SandpileRecurrenceMembership()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        assert entry.answer in ("recurrent", "transient")


def test_balanced_labels_across_levels():
    task = SandpileRecurrenceMembership()
    for level in range(7):
        task.config.set_level(level)
        counts = {"recurrent": 0, "transient": 0}
        for _ in range(40):
            entry = task.generate_example()
            counts[entry.answer] += 1
        assert counts["recurrent"] > 0
        assert counts["transient"] > 0
