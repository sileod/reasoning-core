import random
import sys
from types import SimpleNamespace

import pytest

from scripts import build_contrastive_evals as builder


def mmlu_row(question, subject="science", choices=("water", "oxygen"), answer=0):
    return dict(question=question, subject=subject, choices=list(choices), answer=answer)


def test_mmlu_deduplicates_reordered_options_and_removes_conflicting_labels(monkeypatch):
    rows = [
        mmlu_row("First question"),
        mmlu_row("First question", choices=("oxygen", "water"), answer=1),
        mmlu_row("Conflicting question"),
        mmlu_row("Conflicting question", answer=1),
        mmlu_row("Repeated choices", choices=("water", "water")),
        mmlu_row("Empty choice", choices=("water", "")),
        mmlu_row("Second question", subject="history"),
    ]
    monkeypatch.setattr(builder, "_load", lambda *args, **kwargs: rows)
    result = list(builder.build_mmlu_all_nomenu_cloze(10, random.Random(43)))
    assert {row["prompt"] for row in result} == {
        "First question\nAnswer:", "Second question\nAnswer:"
    }
    assert all(row["answer"] == "water" == row["choices"][row["answer_idx"]]
               for row in result)
    assert result == list(builder.build_mmlu_all_nomenu_cloze(10, random.Random(43)))


def test_mmlu_interleaves_subjects_before_limiting(monkeypatch):
    rows = [mmlu_row(f"Question {subject} {i}", subject=subject)
            for subject in ("a", "b", "c") for i in range(5)]
    monkeypatch.setattr(builder, "_load", lambda *args, **kwargs: rows)
    result = list(builder.build_mmlu_all_nomenu_cloze(6, random.Random(43)))
    assert [row["subject"] for row in result] == ["a", "b", "c", "a", "b", "c"]


@pytest.mark.parametrize("answer", [-1, 2])
def test_mmlu_rejects_invalid_gold_index(monkeypatch, answer):
    monkeypatch.setattr(builder, "_load", lambda *args, **kwargs: [mmlu_row("Q", answer=answer)])
    with pytest.raises(ValueError, match="gold index"):
        list(builder.build_mmlu_all_nomenu_cloze(1, random.Random(43)))


def test_loader_requires_and_passes_revision(monkeypatch):
    calls = []
    monkeypatch.setitem(sys.modules, "datasets", SimpleNamespace(
        load_dataset=lambda *args, **kwargs: calls.append((args, kwargs))))
    builder._load("cais/mmlu", "all", split="test")
    assert calls == [(("cais/mmlu", "all"), dict(
        split="test", revision=builder.REVISIONS["cais/mmlu"]))]
    with pytest.raises(KeyError):
        builder._load("unregistered/source")
    assert len(calls) == 1


def test_cli_checks_all_outputs_before_building(monkeypatch, tmp_path):
    existing = tmp_path / "piqa_eval.jsonl"
    existing.write_text("frozen bytes\n")
    monkeypatch.setattr(sys, "argv", ["build", "--tasks", "boolq", "piqa",
                                      "--output-dir", str(tmp_path)])
    monkeypatch.setitem(builder.BUILDERS, "boolq", lambda *args: pytest.fail("download started"))
    with pytest.raises(FileExistsError):
        builder.main()
    assert existing.read_text() == "frozen bytes\n"
    assert not (tmp_path / "boolq_eval.jsonl").exists()
