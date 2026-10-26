import random
import sys
from types import SimpleNamespace

import pytest

from scripts import build_contrastive_evals as builder


def row(inputs, options=("water", "oxygen"), label=0):
    return dict(inputs=inputs, labels=label, **{f"choice{i}": o for i, o in enumerate(options)})


def test_items_deduplicate_reordered_options_and_drop_conflicts_and_hidden_labels():
    d = {"validation": [row("First"), row("First", ("oxygen", "water"), 1), row("Conflict"),
                        row("Conflict", label=1), row("Repeated", ("water", "water")), row("Empty", ("water", ""))],
         "test": [row("Hidden", label=-1), row("Padded", ("water", "oxygen", None), 0), row("Second")],
         "train": [row("Trained on")]}
    items = builder._items(d, ("validation", "test"))
    assert sorted(items) == [("First", ["water", "oxygen"], "water"), ("Padded", ["water", "oxygen"], "water"),
                             ("Second", ["water", "oxygen"], "water")]


def test_options_keep_numeric_order_past_ten():
    options = [f"o{i}" for i in range(12)]
    assert builder._items({"test": [row("Q", options, 11)]}, ("test",)) == [("Q", options, "o11")]


def test_rebalance_keeps_lever_items_at_chance():
    rng = random.Random(0)
    rows = [builder._row("p", "gold", ["a", "b", "c"], rng) for _ in range(4000)]
    hits = list(builder.rebalance(rows, lambda r: "gold" if rows.index(r) % 2 else "a", random.Random(1)))
    share = sum(rows.index(r) % 2 for r in hits) / len(hits)
    assert abs(share - 0.25) < 0.03                       # the picker is right at chance after rebalancing


def test_winogrande_partial_form(monkeypatch):
    item = builder._row("Tom gave Ben the ball because _ was done playing.", "Tom", ["Ben"], random.Random(0), False)
    monkeypatch.setattr(builder, "tasksource_rows", lambda *a, **k: iter([item]))
    (out,) = builder._winogrande(1, random.Random(0))
    assert out["prompt"] == "Tom gave Ben the ball because"
    assert sorted(out["choices"]) == ["Ben was done playing.", "Tom was done playing."]
    assert out["answer"] == "Tom was done playing." and out["choices"][out["answer_idx"]] == out["answer"]


def test_every_named_source_is_pinned():
    assert all(repo is None or len(builder.REVISIONS[repo]) == 40 for _, repo, _, _ in builder.LEGS.values())


def test_loader_requires_and_passes_revision(monkeypatch):
    calls = []
    monkeypatch.setitem(sys.modules, "datasets", SimpleNamespace(
        load_dataset=lambda *args, **kwargs: calls.append((args, kwargs))))
    builder._load("EleutherAI/hendrycks_math", "algebra", split="test")
    assert calls == [(("EleutherAI/hendrycks_math", "algebra"), dict(
        split="test", revision=builder.REVISIONS["EleutherAI/hendrycks_math"]))]
    with pytest.raises(KeyError):
        builder._load("unregistered/source")
    assert len(calls) == 1


def test_cli_checks_all_outputs_before_building(monkeypatch, tmp_path):
    existing = tmp_path / "piqa_eval.jsonl"
    existing.write_text("frozen bytes\n")
    monkeypatch.setattr(sys, "argv", ["build", "--tasks", "siqa", "piqa", "--output-dir", str(tmp_path)])
    monkeypatch.setitem(builder.BUILDERS, "siqa", lambda *args: pytest.fail("download started"))
    with pytest.raises(FileExistsError):
        builder.main()
    assert existing.read_text() == "frozen bytes\n"
    assert not (tmp_path / "siqa_eval.jsonl").exists()
