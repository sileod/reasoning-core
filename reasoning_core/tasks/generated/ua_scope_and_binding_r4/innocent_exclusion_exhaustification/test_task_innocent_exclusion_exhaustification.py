import random

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.innocent_exclusion_exhaustification.task_innocent_exclusion_exhaustification import (
    InnocentExclusionExhaustification as TaskCls,
    _compute_gold,
)


def _parse(answer):
    s = answer.strip()
    if not (s.startswith("[") and s.endswith("]")):
        return None
    inner = s[1:-1].strip()
    if inner == "":
        return []
    return [int(x) for x in inner.split(",")]


def test_self_consistent_across_levels():
    task = TaskCls()
    for level in list(range(7)):
        cfg = TaskCls.config_cls()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(30):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_gold_recomputed():
    task = TaskCls()
    cfg = TaskCls.config_cls()
    cfg.set_level(3)
    task.config = cfg
    for _ in range(50):
        entry = task.generate_example()
        got = _parse(entry.answer)
        gold = _compute_gold(entry.metadata["prejacent_worlds"], entry.metadata["alternatives"])
        assert got == gold


def test_empty_and_junk():
    task = TaskCls()
    cfg = TaskCls.config_cls()
    cfg.set_level(2)
    task.config = cfg
    entry = task.generate_example()
    assert task.score_answer("[]", entry) < 1.0 or _parse(entry.answer) == []
    assert task.score_answer("junk", entry) == 0.0
    assert task.score_answer("", entry) == 0.0


def test_metadata_json_serializable():
    import json
    task = TaskCls()
    cfg = TaskCls.config_cls()
    for level in (0, 3, 6):
        cfg.set_level(level)
        task.config = cfg
        entry = task.generate_example()
        json.dumps(entry.metadata)


def test_both_answer_regimes_exist():
    task = TaskCls()
    cfg = TaskCls.config_cls()
    cfg.set_level(1)
    task.config = cfg
    sizes = set()
    for _ in range(200):
        entry = task.generate_example()
        sizes.add(len(_parse(entry.answer)))
    assert len(sizes) >= 2
