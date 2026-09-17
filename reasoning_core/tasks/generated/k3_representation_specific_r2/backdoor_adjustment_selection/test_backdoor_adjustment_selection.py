import json
from itertools import combinations
from unittest.mock import patch

import networkx as nx
import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_representation_specific_r2.backdoor_adjustment_selection.backdoor_adjustment_selection import (
    BackdoorAdjustmentSelection,
    TASK_META,
    _backdoor_graph,
    _backdoor_valid,
    _canonical_answer,
    _moral_valid,
)


def _graph(edges, nodes=()):
    graph = nx.DiGraph(edges)
    graph.add_nodes_from(["X", "Y", *nodes])
    return graph


def _path_valid(graph, selected):
    selected = set(selected)
    if selected & nx.descendants(graph, "X"):
        return False
    cut = _backdoor_graph(graph)
    for path in nx.all_simple_paths(cut.to_undirected(), "X", "Y"):
        active = True
        for previous, node, following in zip(path, path[1:], path[2:]):
            collider = cut.has_edge(previous, node) and cut.has_edge(following, node)
            if collider:
                if not (selected & ({node} | nx.descendants(cut, node))):
                    active = False
                    break
            elif node in selected:
                active = False
                break
        if active:
            return False
    return True


@pytest.mark.parametrize("edges,candidates,expected", [
    ([("a", "X"), ("a", "Y"), ("X", "Y")], ["a"], ("a",)),
    ([("u", "X"), ("u", "Y"), ("X", "Y")], ["a"], None),
    ([("u", "a"), ("a", "X"), ("u", "b"), ("b", "Y")], ["a", "b"], ("a",)),
    ([("i", "X"), ("X", "m"), ("m", "Y"), ("X", "c"), ("Y", "c")], ["i", "m", "c"], ()),
    ([("a", "X"), ("a", "b"), ("a", "c"), ("b", "Y"), ("c", "Y")], ["a", "b", "c"], ("a",)),
    ([("a", "X"), ("b", "X"), ("a", "z"), ("b", "z"), ("z", "Y")], ["a", "b", "z"], ("z",)),
    ([("X", "Y")], ["a", "b"], ()),
])
def test_hand_solved_selection(edges, candidates, expected):
    graph = _graph(edges, candidates)
    assert _canonical_answer(graph, candidates) == expected
    assert _canonical_answer(graph, candidates, _moral_valid) == expected
    assert _canonical_answer(graph, candidates, _path_valid) == expected


def test_collider_and_descendant_open_a_path():
    graph = _graph([("a", "X"), ("a", "c"), ("b", "c"), ("b", "Y"), ("c", "d")])
    for verifier in (_backdoor_valid, _moral_valid, _path_valid):
        assert verifier(graph, ())
        assert not verifier(graph, ("c",))
        assert not verifier(graph, ("d",))
        assert verifier(graph, ("a", "d"))


def test_original_descendants_are_forbidden():
    graph = _graph([("X", "m"), ("m", "Y")])
    assert nx.is_d_separator(_backdoor_graph(graph), {"X"}, {"Y"}, {"m"})
    assert not _backdoor_valid(graph, ("m",))
    assert not _moral_valid(graph, ("m",))


def test_all_small_ordered_dags_against_active_paths():
    order = ["a", "X", "b", "Y", "c"]
    possible = list(combinations(order, 2))
    for mask in range(1 << len(possible)):
        graph = _graph([edge for i, edge in enumerate(possible) if mask & (1 << i)], order)
        for size in range(4):
            for selected in combinations(["a", "b", "c"], size):
                expected = _path_valid(graph, selected)
                assert _backdoor_valid(graph, selected) == expected
                assert _moral_valid(graph, selected) == expected


@pytest.mark.parametrize("level", [0, 2, 3, 5, 6])
def test_generated_gold_and_prompt_roundtrip(level):
    task = BackdoorAdjustmentSelection()
    task.config.set_level(level)
    for _ in range(8):
        entry = task.generate_entry()
        metadata = json.loads(json.dumps(entry.metadata))
        assert task.render_prompt(metadata) == task.render_prompt(entry.metadata)
        graph = _graph(metadata["edges"], metadata["nodes"])
        expected = _canonical_answer(graph, metadata["candidates"], _path_valid)
        assert metadata["gold_set"] == (None if expected is None else list(expected))
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer("  " + entry.answer + " .", entry) == 1.0
        assert not set(metadata["candidates"]) & set(metadata["unavailable"])
        assert set(metadata["nodes"]) == set(metadata["candidates"] + metadata["unavailable"] + ["X", "Y"])


@pytest.mark.parametrize("gold", ["none", "impossible", "age", "age, bmi"])
def test_scoring_is_strict_and_stateless(gold):
    class ForbiddenSelf:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = Entry(metadata={}, answer=gold)
    score = BackdoorAdjustmentSelection.score_answer
    assert score(ForbiddenSelf(), gold, entry) == 1.0
    for bad in ["", " ", ",", "...", "junk", None, [], {}, "age, age", "bmi, age", ",age", "age,"]:
        assert score(ForbiddenSelf(), bad, entry) == 0.0


@pytest.mark.parametrize("regime", ["none", "set", "impossible"])
@pytest.mark.parametrize("level", [0, 3, 6])
def test_each_regime_at_each_endpoint(regime, level):
    task = BackdoorAdjustmentSelection()
    task.config.set_level(level)
    with patch("random.choices", return_value=[regime]):
        entry = task.generate_entry()
    assert (entry.answer not in ("none", "impossible")) if regime == "set" else entry.answer == regime


def test_difficulty_and_provenance():
    task = BackdoorAdjustmentSelection()
    task.config.set_level(0)
    low = task.config.n_covariates
    task.config.set_level(6)
    assert task.config.n_covariates > low
    task.config.set_level(0)
    assert task.config.n_covariates == low
    assert TASK_META["hypothesis"] == "P006"
    assert TASK_META["parent_source_id"] is None


def test_saved_prompts_determine_their_answers():
    from pathlib import Path
    from reasoning_core.tasks.generated.k3_representation_specific_r2.backdoor_adjustment_selection.sanitize_samples_P006v3 import verify_samples

    text = Path(__file__).with_name("samples_P006v3.md").read_text()
    assert verify_samples(text) == 6
