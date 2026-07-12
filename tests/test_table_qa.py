from datetime import date

import numpy as np

from reasoning_core.tasks.table_qa import TableQA, canonical_scalar


def test_canonical_scalar_conventions():
    assert canonical_scalar(date(2026, 7, 12)) == "2026-07-12"
    assert canonical_scalar(np.bool_(True)) == "true"
    assert canonical_scalar(False) == "false"
    assert canonical_scalar(np.nan) == "NULL"
    assert canonical_scalar(1234.5) == "1234.5"


def scalar_prompt(kind):
    return TableQA().render_prompt({
        "is_scalar": True,
        "scalar_kind": kind,
        "tables": ["x"],
        "query": "SELECT 1",
    })


def test_table_qa_states_only_the_relevant_scalar_convention():
    assert "YYYY-MM-DD" in scalar_prompt("date")
    assert "`true` or `false`" in scalar_prompt("bool")
    assert "YYYY-MM-DD" not in scalar_prompt("bool")
    assert "literal NULL" in scalar_prompt("null")
    assert "without display formatting" in scalar_prompt("number")
    assert "The answer is the result as a single value." in scalar_prompt(None)
