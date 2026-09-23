import random

from reasoning_core.tasks.generated.k3_non_local_structured_r4.fluent_persistence_windows.fluent_persistence_windows import (
    FluentPersistenceWindows,
)


def test_generate_and_score():
    random.seed(1)
    task = FluentPersistenceWindows()
    seen = set()
    for _ in range(200):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        seen.add(ex.metadata["mode"])
    assert {"holds", "first", "last", "set"} <= seen


def test_all_levels():
    random.seed(2)
    task = FluentPersistenceWindows()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert ex.prompt is not None and len(ex.prompt) < 2048


def test_garbage_answers():
    random.seed(3)
    task = FluentPersistenceWindows()
    for _ in range(100):
        ex = task.generate_example()
        assert task.score_answer("banana", ex) < 1.0
        assert task.score_answer("", ex) < 1.0


def test_dedup_key_stable():
    random.seed(4)
    task = FluentPersistenceWindows()
    ex = task.generate_example()
    k1 = task.deduplication_key(ex)
    ex2 = ex
    k2 = task.deduplication_key(ex2)
    assert k1 == k2
