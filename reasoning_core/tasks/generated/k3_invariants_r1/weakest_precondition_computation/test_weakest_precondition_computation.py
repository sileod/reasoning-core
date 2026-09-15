import importlib.util
import json
import os
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_SPEC = importlib.util.spec_from_file_location(
    "wpc_module", _HERE / "weakest_precondition_computation.py")
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)

Task = _MOD.Task
WeakestPreconditionComputation = _MOD.WeakestPreconditionComputation
Entry = None


def _entry_check(task, x):
    assert x is not None
    assert hasattr(x, "answer")
    assert task.score_answer(x.answer, x) == 1.0


def test_generate_and_score():
    task = WeakestPreconditionComputation()
    task.config.set_level(3)
    x = task.generate_example()
    assert isinstance(x.answer, str) and x.answer
    assert task.score_answer(x.answer, x) == 1.0


def test_all_levels_produce():
    task = WeakestPreconditionComputation()
    for lvl in range(0, 7):
        task.config.set_level(lvl)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_junk_does_not_score():
    task = WeakestPreconditionComputation()
    task.config.set_level(0)
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("banana junk", x) < 1.0


def test_metadata_json_serializable():
    task = WeakestPreconditionComputation()
    task.config.set_level(5)
    x = task.generate_example()
    json.dumps(x.metadata)
