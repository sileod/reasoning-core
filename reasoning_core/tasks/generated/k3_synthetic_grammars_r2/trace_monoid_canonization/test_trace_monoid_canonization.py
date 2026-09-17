import random
from itertools import permutations, product

import pytest

from reasoning_core.tasks.generated.k3_synthetic_grammars_r2.trace_monoid_canonization.trace_monoid_canonization import (
    TraceMonoidCanonization,
    _count_interleavings,
    _depth_layers,
    _interleave,
    _relation,
    _strip_layers,
    _trace_class,
)


@pytest.fixture(autouse=True)
def preserve_rng():
    state = random.getstate()
    yield
    random.setstate(state)


@pytest.mark.parametrize('level', range(7))
def test_roundtrip_levels(level):
    random.seed(382564971 + level)
    task = TraceMonoidCanonization()
    task.config.set_level(level)
    for _ in range(8):
        entry = task.generate_entry()
        assert task.score_answer(entry.answer, entry) == 1.0
        for junk in ('', 'junk', None, '12 extra'):
            assert task.score_answer(junk, entry) == 0.0
        assert entry.metadata['word'] != entry.metadata['seed']
        assert entry.metadata['class_size'] >= 3
        assert entry.metadata['word'] in task.render_prompt(entry.metadata)


def test_all_modes():
    random.seed(382564971)
    task = TraceMonoidCanonization()
    modes = {task.generate_entry().metadata['mode'] for _ in range(40)}
    assert modes == {'canonical', 'layers', 'size'}


def test_nonconfluent_adjacent_sort_regression():
    relation = _relation('abc', [('a', 'b'), ('b', 'c')])
    assert _interleave('cab', relation) == 'bca'
    assert _trace_class('cab', relation) == {'cab', 'cba', 'bca'}
    assert _depth_layers('cab', relation) == ['bc', 'a']


def test_exhaustive_small_words():
    pairs = [('a', 'b'), ('a', 'c'), ('b', 'c')]
    for flags in product((False, True), repeat=3):
        relation = _relation('abc', [p for p, flag in zip(pairs, flags) if flag])
        for letters in product('abc', repeat=4):
            word = ''.join(letters)
            cls = _trace_class(word, relation)
            assert _interleave(word, relation) == min(cls)
            assert _count_interleavings(word, relation) == len(cls)
            layers = _depth_layers(word, relation)
            assert layers == _strip_layers(word, relation)
            assert ''.join(layers) in cls
            assert all(_depth_layers(w, relation) == layers for w in sorted(cls))


def test_verifier_cap_rejects():
    relation = _relation('abc', [('a', 'b'), ('a', 'c'), ('b', 'c')])
    assert _trace_class('abc', relation, cap=2) is None
    assert _count_interleavings('aabbcc', relation) == 90


def test_topological_canonicalization_with_repeated_labels():
    relation = _relation('abc', [('a', 'b'), ('b', 'c')])
    for perm in permutations('aabc'):
        word = ''.join(perm)
        assert _interleave(word, relation) == min(_trace_class(word, relation))
