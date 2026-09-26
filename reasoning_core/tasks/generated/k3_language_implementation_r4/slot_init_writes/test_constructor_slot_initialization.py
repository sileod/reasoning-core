import json
import re

from reasoning_core.tasks.generated.k3_language_implementation_r4.slot_init_writes.constructor_slot_initialization import (
    SlotInitWrites,
)


def _norm(s):
    return "".join(str(s).split())


def _reconstruct_answer(meta):
    field_values = {}
    writes = []
    for name, v in zip(meta["pre_names"], meta["pre_values"]):
        writes.append((name, v))
        field_values[name] = v
    for name, arg in zip(meta["base_names"], meta["base_args"]):
        if arg[0] == "lit":
            v = arg[1]
        else:
            v = field_values[arg[1]]
        writes.append((name, v))
        field_values[name] = v
    for name, expr in zip(meta["post_names"], meta["post_exprs"]):
        if expr[0] == "lit":
            v = expr[1]
        else:
            v = field_values[expr[1]]
        writes.append((name, v))
        field_values[name] = v
    for field, v in meta["overwrites"]:
        writes.append((field, v))
    return ", ".join(f"{f}={v}" for f, v in writes)


def test_gold_scores_one():
    task = SlotInitWrites()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_reconstructs_from_metadata():
    task = SlotInitWrites()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(40):
            ex = task.generate_example()
            expected = _reconstruct_answer(ex.metadata)
            assert _norm(ex.answer) == _norm(expected), (ex.answer, expected)


def test_answer_values_all_in_domain():
    task = SlotInitWrites()
    task.config.set_level(4)
    for _ in range(100):
        ex = task.generate_example()
        assert re.fullmatch(
            r"(?:[A-Za-z_]+\w*=\d+)(?:, [A-Za-z_]+\w*=\d+)*", ex.answer
        ), ex.answer
        for field in re.findall(r"(\d+)", ex.answer):
            assert 1 <= int(field) <= 60


def test_junk_not_scored():
    task = SlotInitWrites()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1
    assert task.score_answer("junk!!", ex) < 1
    assert task.score_answer("alpha=1, beta=2", ex) < 1 or "alpha" in ex.answer


def test_difficulty_changes_config():
    task = SlotInitWrites()
    task.config.set_level(0)
    c0 = task.config.overwrite_prob
    task.config.set_level(6)
    assert task.config.overwrite_prob > c0
    assert task.config.dep_prob > 0.22


def test_always_reachable():
    task = SlotInitWrites()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert ex.answer and "super().__init__(" in ex.prompt
        assert len(ex.metadata["base_names"]) >= 1
        assert len(ex.metadata["pre_names"]) >= 1
        assert len(ex.metadata["post_names"]) >= 1


def test_overwrite_and_dependency_variety():
    task = SlotInitWrites()
    task.config.set_level(5)
    saw_overwrite = False
    saw_dep = False
    for _ in range(300):
        ex = task.generate_example()
        if ex.metadata["overwrites"]:
            saw_overwrite = True
        for arg in ex.metadata["base_args"]:
            if arg[0] == "ref":
                saw_dep = True
        for expr in ex.metadata["post_exprs"]:
            if expr[0] == "ref":
                saw_dep = True
    assert saw_overwrite
    assert saw_dep


def test_json_safe():
    task = SlotInitWrites()
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))
    assert "writes" in ex.metadata
