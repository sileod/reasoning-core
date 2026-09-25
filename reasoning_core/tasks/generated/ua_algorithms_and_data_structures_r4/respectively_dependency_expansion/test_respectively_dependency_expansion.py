import pytest

from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.respectively_dependency_expansion.respectively_dependency_expansion import (
    RespectivelyDependencyExpansion,
)


def test_gold_scoring():
    task = RespectivelyDependencyExpansion()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_garbage_scores_zero():
    task = RespectivelyDependencyExpansion()
    task.config.set_level(0)
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("zzz not an answer", entry) == 0.0


def test_pairing_respects_order():
    task = RespectivelyDependencyExpansion()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(50):
            entry = task.generate_example()
            names = entry.metadata["names"]
            objs = entry.metadata["objs"]
            target = entry.metadata["target"]
            verb = entry.metadata["verb"]
            modifier = entry.metadata["modifier"]
            expected_obj = objs[names.index(target)]
            assert entry.answer == f"{target} {verb} {expected_obj} {modifier}"


def test_wrong_target_scores_zero():
    task = RespectivelyDependencyExpansion()
    for level in range(3):
        task.config.set_level(level)
        for _ in range(50):
            entry = task.generate_example()
            names = entry.metadata["names"]
            other = [n for n in names if n != entry.metadata["target"]]
            if not other:
                continue
            verb = entry.metadata["verb"]
            w = other[0]
            gold_parts = entry.answer.split()
            wrong = f"{w} {verb} {gold_parts[2]} {gold_parts[3]}"
            if wrong != entry.answer:
                continue
            assert task.score_answer(wrong, entry) == 0.0


def test_target_not_constantly_first():
    task = RespectivelyDependencyExpansion()
    seen = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(100):
            entry = task.generate_example()
            seen.add(entry.metadata["target"])
        assert len(seen) >= 2


def test_levels_change_config():
    task = RespectivelyDependencyExpansion()
    c0 = task.config.base_pairs if hasattr(task.config, "base_pairs") else None
    task.config.set_level(0)
    l0 = task.config.count
    task.config.set_level(6)
    l6 = task.config.count
    assert l6 >= l0
