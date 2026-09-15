import random

from reasoning_core.tasks.generated.wave12.truth_maintenance_revision.truth_maintenance_revision import (
    TruthMaintenanceRevision,
    TruthMaintenanceConfig,
)


def test_gold_scores_one():
    random.seed(1)
    task = TruthMaintenanceRevision()
    for _ in range(30):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_and_empty_score_zero():
    random.seed(2)
    task = TruthMaintenanceRevision()
    e = task.generate_example()
    assert task.score_answer("", e) < 1.0
    assert task.score_answer("garbage", e) < 1.0


def test_difficulty_changes_config():
    cfg = TruthMaintenanceConfig()
    base = (cfg.num_facts, cfg.max_premises, cfg.max_revisions)
    cfg_hi = TruthMaintenanceConfig()
    cfg_hi.set_level(4)
    hi = (cfg_hi.num_facts, cfg_hi.max_premises, cfg_hi.max_revisions)
    assert base != hi


def test_answer_is_sorted_ids():
    random.seed(3)
    task = TruthMaintenanceRevision()
    e = task.generate_example()
    ids = [int(x) for x in e.answer.split(",")]
    assert ids == sorted(ids)
    assert all(1 <= x <= e.metadata["num_facts"] for x in ids)
