import random

from reasoning_core.tasks.generated.wave12.schema_migration_execution.schema_migration_execution import (
    MigrationConfig,
    SchemaMigrationExecution,
)


def test_gold_scores_one():
    random.seed(469753138)
    task = SchemaMigrationExecution()
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_balanced_binary_answers():
    random.seed(7)
    task = SchemaMigrationExecution()
    vals = set()
    for _ in range(80):
        ex = task.generate_example()
        vals.add(ex.answer)
    assert len(vals) > 10


def test_difficulty_changes():
    c = MigrationConfig()
    base = (c.n_fields, c.n_ops)
    c.set_level(3)
    assert (c.n_fields, c.n_ops) != base


def test_junk_scores_zero():
    random.seed(3)
    task = SchemaMigrationExecution()
    ex = task.generate_example()
    assert task.score_answer('', ex) == 0.0
    assert task.score_answer('garbage', ex) < 1.0
