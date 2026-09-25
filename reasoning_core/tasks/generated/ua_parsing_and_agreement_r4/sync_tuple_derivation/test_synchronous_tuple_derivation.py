import json
import random

import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_parsing_and_agreement_r4.synchronous_tuple_derivation.synchronous_tuple_derivation import (
    SyncTupleDerivationV2,
    SyncTupleConfig,
    _interleave,
    _wrap,
    _render,
)

MOD = "reasoning_core.tasks.generated.ua_parsing_and_agreement_r4.synchronous_tuple_derivation.synchronous_tuple_derivation"


def _module():
    from reasoning_core.template import register_dataset
    import importlib
    return importlib.import_module(MOD)


def test_interleave():
    assert _interleave(["a", "b"], ["c", "d"]) == ["a", "c", "b", "d"]
    assert _interleave(["a", "b", "c"], ["d", "e"]) == ["a", "d", "b", "e", "c"]
    assert _interleave(["a"], ["b", "c", "d"]) == ["a", "b", "c", "d"]


def test_wrap_render():
    assert _wrap("a", "[") == "[a["
    assert _render(["a", "b"]) == "(a, b)"


def test_module_attrs():
    mod = _module()
    assert mod.TASK_META["idea"] == "synchronous_tuple_derivation (variant 2 of 3)"
    assert "synchronous_tuple_derivation" in mod.TASK_META["changes"]
    assert mod.TASK_META["parent_source_id"] is None
    assert mod.design_choice == SyncTupleDerivationV2.design_choice


def test_summary_single_line():
    s = SyncTupleDerivationV2.summary
    assert isinstance(s, str) and s.strip() == s and "\n" not in s


def test_generate_and_score_all_levels():
    task = SyncTupleDerivationV2()
    for level in range(7):
        ex = task.generate_example(level=level)
        assert isinstance(ex, Entry)
        assert ex.answer in {"a", "b", "c", "d", "e", "f", "g", "h", "x", "y", "z"}
        assert task.score_answer(ex.answer, ex) == 1
        assert task.score_answer("", ex) == 0
        assert task.score_answer("notananswer", ex) == 0
        json.dumps(dict(ex.metadata))


def test_answers_vary_within_level():
    task = SyncTupleDerivationV2()
    answers = {task.generate_example(level=5).answer for _ in range(40)}
    assert len(answers) >= 2, f"constant answer at level 5: {answers}"


def test_config_changes():
    task = SyncTupleDerivationV2()
    base = SyncTupleConfig()
    task.config.set_level(6)
    assert task.config.wrap_steps > base.wrap_steps


def test_gold_domain():
    task = SyncTupleDerivationV2()
    for _ in range(20):
        ex = task.generate_example()
        assert ex.answer in {"a", "b", "c", "d", "e", "f", "g", "h", "x", "y", "z"}
