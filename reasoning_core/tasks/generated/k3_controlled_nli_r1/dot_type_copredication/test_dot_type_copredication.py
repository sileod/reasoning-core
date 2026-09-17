import itertools
import json
import random

import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_controlled_nli_r1.dot_type_copredication.dot_type_copredication import (
    DotTypeCopredicationConfig,
    DotTypeCopredication,
    LABELS,
    _reachable,
    _selected_facet,
    _verify,
)


@pytest.fixture(autouse=True)
def fixed_random():
    state = random.getstate()
    random.seed(3577985643)
    yield
    random.setstate(state)


@pytest.mark.parametrize("level", range(7))
def test_generation_and_balance(level):
    task = DotTypeCopredication()
    task.config.set_level(level)
    counts = dict.fromkeys(LABELS, 0)
    prompts = {}
    for _ in range(200):
        entry = task.generate_entry()
        m = json.loads(json.dumps(entry.metadata))
        facets = m["lexicon"][m["subject"]]
        demands = list(m["predicates"].values())
        _verify(m["types"], m["edges"], facets, demands, entry.answer)
        assert len(m["sentence_order"]) >= 2
        assert set(m["sentence_order"]) == set(m["predicates"])
        prompt = task.render_prompt(m)
        assert len(task.tokenizer.encode(prompt)) < 2048
        assert task.score_answer(entry.answer, entry) == 1.0
        for label in LABELS:
            assert task.score_answer(label, entry) == float(label == entry.answer)
        assert prompts.setdefault(prompt, entry.answer) == entry.answer
        counts[entry.answer] += 1
    assert all(25 < count < 80 for count in counts.values())


@pytest.mark.parametrize("demands, expected", [
    ([["x"], ["y"]], "neither"),
    ([["z"], ["z", "x"]], "both"),
    ([["x"], ["z"]], "A"),
    ([["y"], ["z"]], "B"),
    ([["q"]], "neither"),
    ([["x", "y"], ["z"]], "both"),
])
def test_shared_start_and_alternatives(demands, expected):
    types = ["x", "y", "z", "q"]
    edges = [["x", "z"], ["y", "z"]]
    reachable = _reachable(types, edges)
    assert _selected_facet(demands, ["x", "y"], reachable) == expected
    _verify(types, edges, ["x", "y"], demands, expected)


def test_transitive_directional_and_zero_step_coercion():
    types = ["a", "b", "c", "d", "e"]
    edges = [["a", "c"], ["c", "d"], ["d", "e"], ["b", "e"]]
    reachable = _reachable(types, edges)
    assert _selected_facet([["d"], ["a"]], ["a", "b"], reachable) == "A"
    assert _selected_facet([["e"]], ["a", "b"], reachable) == "both"
    assert _selected_facet([["a"]], ["d", "e"], reachable) == "neither"


def test_exhaustive_small_graphs_against_independent_verifier():
    types = ["a", "b", "c"]
    possible_edges = list(itertools.permutations(types, 2))
    alternatives = [[t] for t in types] + [["a", "b"], ["b", "c"]]
    for bits in itertools.product([False, True], repeat=len(possible_edges)):
        edges = [edge for edge, present in zip(possible_edges, bits) if present]
        reachable = _reachable(types, edges)
        for demands in itertools.product(alternatives, repeat=2):
            answer = _selected_facet(demands, ["a", "b"], reachable)
            _verify(types, edges, ["a", "b"], demands, answer)


def test_verifier_rejects_incorrect_gold():
    with pytest.raises(AssertionError):
        _verify(["a", "b"], [], ["a", "b"], [["a"]], "both")


@pytest.mark.parametrize("junk", ["", "banana", None, 1, [], {}, "A or B", "a", "B."])
def test_mock_self_and_strict_scoring(junk):
    class NoAttributes:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = Entry(metadata={}, answer="A")
    assert DotTypeCopredication.score_answer(NoAttributes(), "A", entry) == 1.0
    assert DotTypeCopredication.score_answer(NoAttributes(), junk, entry) == 0.0


def test_config_monotonic_and_resettable():
    cfg = DotTypeCopredicationConfig()
    sizes = []
    for level in range(7):
        cfg.set_level(level)
        sizes.append((cfg.depth, cfg.n_predicates))
    assert sizes == sorted(sizes)
    assert sizes[0] != sizes[1]
    cfg.set_level(0)
    assert (cfg.depth, cfg.n_predicates) == sizes[0]


def test_seed_reproducibility_and_no_reseeding(monkeypatch):
    task = DotTypeCopredication()
    state = random.getstate()
    task.config.set_level(5)
    first = task.generate_entry()
    random.setstate(state)
    task.config.set_level(5)

    def forbidden(*args, **kwargs):
        raise AssertionError("generation must not reseed")

    monkeypatch.setattr(random, "seed", forbidden)
    second = task.generate_entry()
    assert first.answer == second.answer
    assert first.metadata == second.metadata
    assert task.render_prompt(first.metadata) == task.render_prompt(second.metadata)
