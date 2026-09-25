import random

from reasoning_core.template import Entry

_ENTRY = "reasoning_core.tasks.generated.k3_psychometrics_r5.invented_numeral_evaluation.invented_numeral_evaluation"


def _get_task():
    import importlib
    mod = importlib.import_module(_ENTRY)
    return mod.InventedNumeralEvaluation()


def _check_self_consistent(entry, mod):
    mode = entry.metadata["mode"]
    if mode == "value":
        from reasoning_core.template import Config
        val = mod._parse(entry.metadata["s"], {s: v for s, v in entry.metadata["morphemes"]})
        assert int(entry.answer) == val, (entry.answer, val)
    elif mode == "canonical":
        assert entry.answer in entry.metadata["morphemes"] or len(entry.answer) >= 1
    else:
        assert entry.answer in ("yes", "no")


def test_generate_and_score_value():
    task = _get_task()
    for _ in range(50):
        entry = task.generate_example()
        assert entry.answer is not None
        assert task.score_answer(entry.answer, entry) == 1.0


def test_garbage_scores_low():
    task = _get_task()
    for _ in range(50):
        entry = task.generate_example()
        assert task.score_answer("", entry) < 1.0
        assert task.score_answer("not an answer", entry) < 1.0


def test_all_modes_seen():
    task = _get_task()
    modes = set()
    for _ in range(300):
        e = task.generate_example()
        modes.add(e.metadata["mode"])
    assert modes == {"value", "canonical", "valid"}


def test_valid_balanced():
    task = _get_task()
    counts = {"yes": 0, "no": 0}
    for _ in range(200):
        e = task.generate_example()
        if e.metadata["mode"] == "valid":
            counts[e.answer] += 1
    assert counts["yes"] > 0 and counts["no"] > 0


def test_metadata_jsonable():
    import json
    task = _get_task()
    for _ in range(20):
        e = task.generate_example()
        json.dumps(e.metadata)


def test_difficulty_changes():
    task = _get_task()
    task.config.set_level(0)
    c0 = task.config.base_morphemes
    task.config.set_level(6)
    c6 = task.config.base_morphemes
    assert c6 >= c0
