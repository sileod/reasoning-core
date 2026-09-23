import random

from reasoning_core.tasks.generated.k3_formal_logic_r4.call_by_need_thunk_accounting.call_by_need_thunk_accounting import (
    CallByNeedThunkAccounting,
    _parse,
)


def test_generate_scores_gold():
    random.seed(1)
    task = CallByNeedThunkAccounting()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(60):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0
            never = entry.metadata["never"]
            roots = set(entry.metadata["roots"])
            demanded = set(entry.metadata["demanded"])
            assert roots <= demanded
            assert set(never) == demanded ^ set(entry.metadata["names"])
            assert 0 < len(never) < len(entry.metadata["names"])


def test_metadata_json_serializable():
    import json

    random.seed(2)
    task = CallByNeedThunkAccounting()
    task.config.set_level(4)
    entry = task.generate_example()
    json.dumps(entry.metadata)


def test_parse():
    assert _parse("x00, x02") == frozenset({"x00", "x02"})
    assert _parse("none") == frozenset()
    assert _parse("") == frozenset()


def test_score_rejects_wrong():
    random.seed(3)
    task = CallByNeedThunkAccounting()
    task.config.set_level(3)
    entry = task.generate_example()
    assert task.score_answer("some random thing", entry) == 0.0
    assert task.score_answer("", entry) == 0.0
