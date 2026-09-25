import json
import random

import pytest

from reasoning_core.tasks.generated.ua_inference_modes_r4.cyclic_proof_closure.cyclic_proof_closure import (
    _fmt, _ground_seq, _unify, _valid_ancestors, CyclicProofClosure,
    CyclicProofClosureConfig,
)


@pytest.fixture(autouse=True)
def seeded():
    random.seed(12345)
    yield


def test_unify_basic():
    leaf = [('p', ('v0',)), ('q', ('c5',))]
    ancestor = [('q', ('c5',)), ('p', ('c9',))]
    assert _unify(ancestor, leaf) is True


def test_unify_no_match():
    leaf = [('p', ('v0',))]
    ancestor = [('q', ('c5',))]
    assert _unify(ancestor, leaf) is False


def test_unify_count_mismatch():
    leaf = [('p', ('v0',))]
    ancestor = [('p', ('c1',)), ('p', ('c2',))]
    assert _unify(ancestor, leaf) is False


def test_unify_conflicting_constants():
    leaf = [('p', ('c3',))]
    ancestor = [('p', ('c9',))]
    assert _unify(ancestor, leaf) is False


def test_task_roundtrip_all_levels():
    for level in (0, 2, 5, 6):
        task = CyclicProofClosure()
        for _ in range(20):
            ex = task.generate_example(level=level)
            assert ex.answer in ('impossible',) or ex.answer.isdigit()
            assert task.score_answer(ex.answer, ex) == 1.0
            d = json.loads(json.dumps(dict(ex.metadata)))
            assert d['open_leaf'] == ex.metadata['open_leaf']


def test_gold_consistent_with_checker():
    task = CyclicProofClosure()
    for _ in range(200):
        ex = task.generate_example()
        md = ex.metadata
        seq = [list(n['seq']) for n in md['nodes']]
        parent = [-1] * len(seq)
        for n in md['nodes']:
            for c in n['children']:
                parent[c] = n['id']
        L = md['open_leaf']
        valid = _valid_ancestors(seq, parent, L)
        if ex.answer == 'impossible':
            assert valid == []
        else:
            assert valid == [int(ex.answer)]


def test_balanced_labels():
    task = CyclicProofClosure()
    counts = {'impossible': 0, 'node': 0}
    for _ in range(400):
        ex = task.generate_example()
        if ex.answer == 'impossible':
            counts['impossible'] += 1
        else:
            counts['node'] += 1
    total = counts['impossible'] + counts['node']
    assert 0.25 < counts['impossible'] / total < 0.75


def test_garbage_scores_zero():
    task = CyclicProofClosure()
    ex = task.generate_example()
    assert task.score_answer('', ex) < 1.0
    assert task.score_answer('zzz999', ex) < 1.0
    assert task.score_answer('import fakemodule', ex) < 1.0


def test_config_difficulty_changes():
    cfg = CyclicProofClosureConfig()
    before = (cfg.min_nodes, cfg.max_nodes)
    cfg.set_level(3)
    after = (cfg.min_nodes, cfg.max_nodes)
    assert before != after


def test_nonleaf_seqs_distinct():
    task = CyclicProofClosure()
    for _ in range(50):
        ex = task.generate_example()
        L = ex.metadata['open_leaf']
        seqs = [tuple(sorted(n['seq'])) for n in ex.metadata['nodes'] if n['id'] != L]
        assert len(set(seqs)) == len(seqs)
