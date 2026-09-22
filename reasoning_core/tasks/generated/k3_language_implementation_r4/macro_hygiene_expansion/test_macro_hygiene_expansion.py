import random
import string

import pytest

from reasoning_core.tasks.generated.k3_language_implementation_r4.macro_hygiene_expansion.macro_hygiene_expansion import (
    MacroHygieneExpansion,
    MacroConfig,
    TASK_META,
    render,
    term_free,
    term_names,
    rename_term,
)


@pytest.fixture
def task():
    return MacroHygieneExpansion()


def test_summary_literal(task):
    assert isinstance(MacroHygieneExpansion.summary, str)
    assert "\n" not in MacroHygieneExpansion.summary
    assert MacroHygieneExpansion.design_choice.startswith(
        "Instances present a macro call in a small lambda calculus")


def test_task_meta():
    assert TASK_META["hypothesis"] == "P002"
    assert TASK_META["parent_source_id"] is None
    assert "variant 1 of 3" in TASK_META["idea"]


def test_config_level_change():
    c = MacroConfig()
    base = MacroConfig()
    c.set_level(3)
    assert c != MacroConfig()
    assert c.level == 3
    assert c.n_macros > base.n_macros


def test_roundtrip(task):
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) != 1.0
        assert task.score_answer("junk !!! ", ex) != 1.0


def test_no_remaining_calls(task):
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert "M" not in ex.answer


def test_weight_naming(task):
    task.config.set_level(4)
    seen_none = False
    seen_some = False
    for _ in range(25):
        ex = task.generate_example()
        if "x_0" in ex.answer or "x_1" in ex.answer:
            seen_some = True
        else:
            seen_none = True
    assert seen_some or task.config.n_macros <= 1


def test_deterministic_under_seed():
    random.seed(1234)
    t1 = MacroHygieneExpansion()
    a = [t1.generate_example().answer for _ in range(5)]
    random.seed(1234)
    t2 = MacroHygieneExpansion()
    b = [t2.generate_example().answer for _ in range(5)]
    assert a == b


def test_term_helpers():
    t = ("lam", "x", ("app", ("var", "x"), ("var", "y")))
    assert term_free(t) == {"y"}
    assert term_names(t) == {"x", "y"}
    r = rename_term(t, "x", "z")
    assert r == ("lam", "z", ("app", ("var", "z"), ("var", "y")))
