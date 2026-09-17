import json
from itertools import product

import numpy as np
import pytest

from reasoning_core.tasks.generated.k3_algorithms_and_data_structures_r1.temporal_connective_equivalence import (
    temporal_connective_equivalence as mod,
)


def test_roundtrip_and_scoring():
    task = mod.TemporalConnectiveEquivalence()
    for level in range(7):
        task.config.set_level(level)
        labels = set()
        for _ in range(24):
            entry = task.generate_example()
            labels.add(entry.answer)
            assert task.score_answer(entry.answer, entry) == 1.0
            assert task.score_answer(" " + entry.answer.upper() + " ", entry) == 1.0
            for junk in ("", "banana", "yes no", None, [], {}):
                assert task.score_answer(junk, entry) == 0.0
            wrong = "no" if entry.answer == "yes" else "yes"
            assert task.score_answer(wrong, entry) == 0.0
            assert mod.TemporalConnectiveEquivalence.score_answer(None, entry.answer, entry) == 1.0
            metadata = json.loads(json.dumps(dict(entry.metadata)))
            assert task.render_prompt(metadata) == task.render_prompt(entry.metadata)
            assert metadata["source_text"] != metadata["target_text"]
            worlds = mod.timelines(tuple(metadata["aspects"]))
            same = np.array_equal(mod.truth_values(metadata["source"], worlds),
                                  mod.truth_values(metadata["target"], worlds))
            assert same == (entry.answer == "yes")
        assert labels == {"yes", "no"}


def test_label_balance_at_endpoints():
    task = mod.TemporalConnectiveEquivalence()
    for level in (0, 3, 6):
        task.config.set_level(level)
        positives = sum(task.generate_entry().answer == "yes" for _ in range(120))
        assert 30 < positives < 90


@pytest.mark.parametrize("aspects", list(product(("durative", "punctual"), repeat=2)))
def test_rewrites_preserve_all_timelines(aspects):
    worlds = mod.timelines(aspects)
    for relation in mod.RELATIONS:
        source = mod.atom(relation, 0, 1)
        for expr in (source, ["not", source],
                     ["not", ["and", source, mod.atom("before", 1, 0)]]):
            for _ in range(8):
                target = mod.restructure(expr)
                assert np.array_equal(mod.truth_values(expr, worlds), mod.truth_values(target, worlds))
                assert mod.solver_equivalent(expr, target, aspects)


def test_punctual_no_sooner_is_symmetric_but_duration_is_not():
    forward = mod.atom("no-sooner", 0, 1)
    reverse = mod.atom("no-sooner", 1, 0)
    assert mod.solver_equivalent(forward, reverse, ("punctual", "punctual"))
    assert not mod.solver_equivalent(forward, reverse, ("durative", "punctual"))


def test_closed_endpoint_and_negation_semantics():
    worlds = np.asarray([[(0, 2), (2, 2)], [(0, 2), (3, 3)], [(0, 2), (1, 1)]])
    expected = {"before": [False, True, False], "after": [False, False, False],
                "until": [True, False, False], "since": [False, False, False],
                "while": [True, False, True], "no-sooner": [True, False, False]}
    for relation, truth in expected.items():
        expr = mod.atom(relation, 0, 1)
        assert mod.truth_values(expr, worlds).tolist() == truth
        assert mod.truth_values(["not", expr], worlds).tolist() == [not t for t in truth]


def test_transitivity_and_de_morgan():
    ab, bc, ac = (mod.atom("before", a, b) for a, b in ((0, 1), (1, 2), (0, 2)))
    chain = ["and", ab, bc]
    assert mod.solver_equivalent(chain, ["and", chain, ac], ("durative",) * 3)
    assert not mod.solver_equivalent(chain, ["and", ab, ac], ("durative",) * 3)
    assert mod.solver_equivalent(["not", ["or", ab, bc]],
                                 ["and", ["not", ab], ["not", bc]], ("punctual",) * 3)


@pytest.mark.parametrize("aspects", list(product(("durative", "punctual"), repeat=2)))
def test_exhaustive_scalar_oracle_and_render_collisions(aspects):
    worlds = mod.timelines(aspects)
    names = [mod.DURATIVE[i] if aspect == "durative" else mod.PUNCTUAL[i]
             for i, aspect in enumerate(aspects)]
    rendered = {}
    for relation, reverse, negate, variant in product(mod.RELATIONS, (False, True), (False, True), (0, 1)):
        a, b = (1, 0) if reverse else (0, 1)
        expr = mod.atom(relation, a, b)
        if negate:
            expr = ["not", expr]
        expected = []
        for world in worlds:
            sa, ea = map(int, world[a])
            sb, eb = map(int, world[b])
            if relation == "before":
                holds = ea < sb
            elif relation == "after":
                holds = eb < sa
            elif relation in ("until", "no-sooner"):
                holds = ea == sb
            elif relation == "since":
                holds = eb == sa
            else:
                holds = max(sa, sb) <= min(ea, eb)
            expected.append(not holds if negate else holds)
        actual = mod.truth_values(expr, worlds)
        assert actual.tolist() == expected
        text = mod.render_expression(expr, names, variant)
        signature = tuple(expected)
        if text in rendered:
            assert rendered[text] == signature
        rendered[text] = signature
        if names[a] in mod.PUNCTUAL:
            assert f"{names[a]} ran since" not in text
            assert f"{names[a]} continued until" not in text


def test_rejection_sampling_is_bounded(monkeypatch):
    monkeypatch.setattr(mod, "sample_expression", lambda *args: ["and", mod.atom("before", 0, 1),
                                                               mod.atom("after", 0, 1)])
    with pytest.raises(RuntimeError, match="Could not sample"):
        mod.TemporalConnectiveEquivalence().generate_entry()


def test_solver_unknown_is_rejected(monkeypatch):
    monkeypatch.setattr(mod.z3.Solver, "check", lambda self: mod.z3.unknown)
    with pytest.raises(RuntimeError, match="did not finish"):
        mod.solver_equivalent(mod.atom("before", 0, 1), mod.atom("after", 1, 0),
                              ("durative", "punctual"))
