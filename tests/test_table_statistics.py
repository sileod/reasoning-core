import pandas as pd
import pytest

from reasoning_core.tasks import table_qa


@pytest.mark.parametrize(
    ("family", "df", "find", "answer", "expected_find", "expected_answer"),
    [
        (
            "column_pearson",
            pd.DataFrame({"x0": [1], "x1": [2], "x2": [3]}),
            "column name most associated with column x0",
            "x1",
            "column name most associated with column x1",
            "x2",
        ),
        (
            "row_pearson",
            pd.DataFrame({"row_id": ["R0", "R1", "R2"], "x0": [1, 2, 3]}),
            "row_id most associated with row R0",
            "R1",
            "row_id most associated with row R1",
            "R2",
        ),
        (
            "label_eta2",
            pd.DataFrame({"label": ["a"], "x0": [1], "x1": [2]}),
            "numeric column name most associated with column label",
            "x0",
            "numeric column name most associated with column label",
            "x1",
        ),
        (
            "categorical_nmi",
            pd.DataFrame({"label": ["a"], "c0": ["a"], "c1": ["b"]}),
            "categorical column name most associated with column label",
            "c0",
            "categorical column name most associated with column label",
            "c1",
        ),
    ],
)
def test_statistics_identifiers_are_permuted_with_query_and_answer(
    monkeypatch, family, df, find, answer, expected_find, expected_answer
):
    monkeypatch.setattr(
        table_qa.random,
        "sample",
        lambda population, count: list(population[1:]) + list(population[:1]),
    )
    renamed, spec = table_qa.permute_statistics_identifiers(
        df,
        {"family": family, "find": find, "answer": answer},
    )

    assert spec["find"] == expected_find
    assert spec["answer"] == expected_answer
    assert expected_answer in set(renamed.columns) | set(renamed.get("row_id", []))
