import itertools
import json
import random
from fractions import Fraction

import networkx as nx
import numpy as np
import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_novel_composition_r2.factor_graph_marginal.factor_graph_marginal import (
    FactorGraphMarginal,
    _eliminate,
    _enumerate,
    _parse_table,
)


@pytest.fixture(autouse=True)
def seeded():
    state = random.getstate()
    random.seed(1234)
    yield
    random.setstate(state)


@pytest.mark.parametrize("level", range(7))
def test_generated_marginals(level):
    task = FactorGraphMarginal()
    task.config.set_level(level)
    for _ in range(8):
        entry = task.generate_example()
        m = entry.metadata
        gold = _parse_table(entry.answer)
        assert task.score_answer(entry.answer, entry) == 1
        assert sum(gold) == 1 and all(0 <= p <= 1 for p in gold)
        assert len(gold) == m.domains[m.query]
        assert set(m.elimination_order) == set(m.domains) - set(m.evidence) - {m.query}
        assert m.weights == _enumerate(m.domains, m.factors, m.evidence, m.query)
        assert _eliminate(m.domains, m.factors, m.evidence, m.query, m.elimination_order[::-1]) == m.weights
        restored = json.loads(json.dumps(m))
        assert task.render_prompt(restored) == entry.prompt
        graph = nx.Graph()
        graph.add_nodes_from(m.domains)
        for i, factor in enumerate(m.factors):
            graph.add_edges_from((f"factor_{i}", v) for v in factor["vars"])
        assert nx.is_tree(graph) == (m.topology == "tree")


def test_hand_computed_conditioning_and_axis_order():
    domains = {"A": 2, "B": 2, "C": 2}
    factors = [
        {"vars": ["B", "A"], "table": [1, 3, 2, 4]},
        {"vars": ["B", "C"], "table": [1, 2, 3, 4]},
        {"vars": ["C"], "table": [2, 1]},
    ]
    assert _eliminate(domains, factors, {"C": 1}, "A", ["B"]) == [10, 22]
    for order in itertools.permutations(["B", "C"]):
        assert _eliminate(domains, factors, {}, "A", list(order)) == [24, 52]
    assert _enumerate(domains, factors, {"C": 1}, "A") == [10, 22]
    assert _enumerate(domains, factors, {}, "A") == [24, 52]


@pytest.mark.parametrize("answer", ["", "junk", "1/0, 2/3", "1/3,,2/3", "1/3,2/3,", "-1/3,4/3", "0.333333,0.666667", "1/3", "2/3,1/3", None, [], "9" * 3000])
def test_reject_invalid_or_wrong(answer):
    entry = Entry(metadata={}, answer="1/3, 2/3")
    assert FactorGraphMarginal.score_answer(None, answer, entry) == 0


def test_scorer_uses_no_self_and_exact_rationals():
    class Forbidden:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = Entry(metadata={}, answer="1/3, 2/3")
    assert FactorGraphMarginal.score_answer(Forbidden(), " 2/6, 4/6 ", entry) == 1
    assert FactorGraphMarginal.score_answer(Forbidden(), "333333/1000000,666667/1000000", entry) == 0
    assert _parse_table("1/3, 2/3") == [Fraction(1, 3), Fraction(2, 3)]


def test_distribution_and_reproducibility():
    task = FactorGraphMarginal()
    task.config.set_level(6)
    entries = [task.generate_entry() for _ in range(60)]
    assert {e.metadata.topology for e in entries} == {"tree", "loopy"}
    assert {len(e.metadata.evidence) for e in entries} == {0, 1, 2}
    assert {len(f["vars"]) for e in entries for f in e.metadata.factors} == {1, 2, 3}
    assert {d for e in entries for d in e.metadata.domains.values()} == {2, 3}
    assert len({tuple(e.metadata.elimination_order) for e in entries}) > 20
    random.seed(1336314872)
    a = task.generate_entry()
    random.seed(1336314872)
    b = task.generate_entry()
    assert a.metadata == b.metadata and a.answer == b.answer


def test_mixed_domain_evidence_and_all_orders():
    domains = {"A": 2, "B": 3, "C": 2, "D": 2}
    factors = [
        {"vars": ["C", "B", "A"], "table": list(range(1, 13))},
        {"vars": ["D", "B"], "table": [3, 1, 5, 2, 4, 1]},
        {"vars": ["A", "D"], "table": [1, 3, 5, 2]},
        {"vars": ["C"], "table": [2, 5]},
    ]
    for evidence in ({}, {"C": 1}, {"A": 0, "D": 1}):
        free = [v for v in domains if v not in evidence and v != "B"]
        gold = _enumerate(domains, factors, evidence, "B")
        for order in itertools.permutations(free):
            assert _eliminate(domains, factors, evidence, "B", list(order)) == gold


def test_generated_factors_are_not_separable_by_variable():
    task = FactorGraphMarginal()
    for _ in range(30):
        m = task.generate_entry().metadata
        for factor in m.factors:
            scope = factor["vars"]
            if len(scope) == 1:
                continue
            shape = tuple(m.domains[v] for v in scope)
            array = np.array(factor["table"], dtype=object).reshape(shape)
            for axis, size in enumerate(shape):
                matrix = np.moveaxis(array, axis, 0).reshape(size, -1)
                assert np.any(matrix * matrix[0, 0] != matrix[:, :1] * matrix[:1, :])


def test_endpoint_prompt_headroom():
    from reasoning_core.runtime import load_tokenizer

    tokenizer = load_tokenizer()
    task = FactorGraphMarginal()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            assert len(tokenizer.encode(entry.prompt)) <= 2048
