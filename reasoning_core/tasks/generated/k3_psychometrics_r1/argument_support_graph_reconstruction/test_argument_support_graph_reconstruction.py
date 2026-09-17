import json
import random

import networkx as nx
import pytest

from reasoning_core.tasks.generated.k3_psychometrics_r1.argument_support_graph_reconstruction.argument_support_graph_reconstruction import (
    ArgumentSupportConfig,
    ArgumentSupportGraphReconstruction,
    _canonical,
    _read_argument,
)
from reasoning_core.template import Entry


@pytest.fixture(autouse=True)
def restore_rng():
    state = random.getstate()
    random.seed(1103)
    yield
    random.setstate(state)


def _make(level):
    config = ArgumentSupportConfig()
    config.set_level(level)
    return ArgumentSupportGraphReconstruction(config=config)


@pytest.mark.parametrize('level', range(7))
def test_roundtrip_and_structure(level):
    task = _make(level)
    answers = set()
    families = set()
    for _ in range(40):
        entry = task.generate_entry()
        metadata = json.loads(json.dumps(entry.metadata))
        head, edges = _read_argument(metadata['argument'], metadata['claims'])
        assert entry.answer == _canonical(edges)
        assert task.score_answer(entry.answer, entry) == 1
        assert task.score_answer('', entry) == 0
        assert task.score_answer('junk', entry) == 0
        assert task.render_prompt(metadata) == task.render_prompt(entry.metadata)
        graph = nx.DiGraph(edges)
        assert nx.is_arborescence(graph.reverse())
        assert graph.out_degree(head) == 0
        assert len(edges) == metadata['n_claims'] - 1
        if metadata['family'] == 'chain':
            assert max(dict(graph.in_degree()).values()) == 1
        else:
            assert max(dict(graph.in_degree()).values()) >= 2
        if metadata['family'] == 'fan':
            assert all(graph.in_degree(node) <= 1 for node in graph if node != head)
        families.add(metadata['family'])
        answers.add(entry.answer)
    assert families == {'chain', 'tree', 'fan'}
    assert len(answers) > 30


@pytest.mark.parametrize('argument', [
    '(ember because frost and tide)',
    '(ember since frost and tide)',
    '(given that frost and tide, ember)',
    '(frost and tide; therefore ember)',
])
def test_all_cue_directions(argument):
    claims = [[3, 'ember'], [2, 'tide'], [1, 'frost']]
    assert _read_argument(argument, claims) == (3, [(1, 3), (2, 3)])


def test_nested_scope_excludes_transitive_edges():
    claims = [[12, 'tide'], [4, 'frost'], [2, 'ember'], [1, 'moss'], [3, 'vent']]
    argument = '((given that (tide since moss), ember) and vent; therefore frost)'
    head, edges = _read_argument(argument, claims)
    assert head == 4
    assert edges == [(1, 12), (2, 4), (3, 4), (12, 2)]
    assert (1, 4) not in edges and (12, 4) not in edges


def test_scoring_canonical_order_and_mock_self():
    entry = Entry(metadata={}, answer='2->3;10->3')

    class NoSelf:
        def __getattribute__(self, name):
            raise AssertionError(name)

    score = ArgumentSupportGraphReconstruction.score_answer
    assert score(NoSelf(), entry.answer, entry) == 1
    assert score(NoSelf(), ' 2->3;10->3\n', entry) == 1
    for bad in ('10->3;2->3', '2->3;2->3;10->3', '3->2;3->10',
                '2->3', '2->3;10->3;', '02->3;10->3', '2->3; 10->3',
                '', 'junk', None, [], {}, 2):
        assert score(NoSelf(), bad, entry) == 0


def test_difficulty_scales_and_resets():
    config = ArgumentSupportConfig()
    config.set_level(0)
    sizes = []
    for level in range(7):
        config.set_level(level)
        sizes.append(config.max_claims)
    assert sizes == sorted(set(sizes))
    config.set_level(0)
    assert config.max_claims == 5


def test_generation_determinism_and_prompt_dependence():
    task = _make(5)
    state = random.getstate()
    first = task.generate_entry()
    random.setstate(state)
    second = task.generate_entry()
    assert first.answer == second.answer
    assert first.metadata == second.metadata
    metadata = dict(first.metadata)
    metadata['edges'] = []
    metadata['family'] = 'ignored'
    assert task.render_prompt(metadata) == task.render_prompt(first.metadata)
    assert _canonical(_read_argument(metadata['argument'], metadata['claims'])[1]) == first.answer
