import itertools
import random

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.betweenness_triple_seriation.betweenness_triple_seriation import (
    BetweennessTripleSeriation,
    _count_orders,
    _parse_count,
    _parse_list,
    _parse_triple,
)

from reasoning_core.template import Entry


def test_all_modes_occur():
    random.seed(3)
    task = BetweennessTripleSeriation()
    modes = set()
    for _ in range(120):
        entry = task.generate_example()
        modes.add(entry.metadata['mode'])
    assert modes == {'multiple', 'unique', 'conflict'}


def test_count_orders_matches_exhaustive():
    n = 5
    for perm in itertools.permutations(range(n)):
        pos = {v: i for i, v in enumerate(perm)}
        triples = []
        for combo in itertools.combinations(range(n), 3):
            p = sorted((pos[x], x) for x in combo)
            triples.append((p[0][1], p[1][1], p[2][1]))
        assert _count_orders(n, triples) == 2


def test_scoring_roundtrip_multiple_levels():
    random.seed(7)
    task = BetweennessTripleSeriation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(15):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0
            assert task.score_answer("", entry) < 1.0
            assert task.score_answer("junk", entry) < 1.0


def test_metadata_json_serializable():
    import json
    random.seed(11)
    task = BetweennessTripleSeriation()
    task.config.set_level(5)
    entry = task.generate_example()
    json.dumps(dict(entry.metadata))
    assert isinstance(entry.answer, str)


def test_count_domain():
    random.seed(13)
    task = BetweennessTripleSeriation()
    task.config.set_level(6)
    seen_positive = False
    for _ in range(60):
        entry = task.generate_example()
        if entry.metadata['mode'] == 'multiple':
            assert int(entry.answer) >= 2
            seen_positive = True
    assert seen_positive


def test_parser_helpers():
    assert _parse_count("12") == 12
    assert _parse_count("x") is None
    assert _parse_list("1,2,3") == (1, 2, 3)
    assert _parse_list("a,b") is None
    assert _parse_triple("(3,1,2)") == (3, 1, 2)
    assert _parse_triple("nope") is None


def test_conflict_is_true_first_conflict():
    random.seed(21)
    task = BetweennessTripleSeriation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            if entry.metadata['mode'] != 'conflict':
                continue
            triples = entry.metadata['triples']
            n = entry.metadata['n']
            assert _count_orders(n, triples) == 0
            assert _count_orders(n, triples[:-1]) == 2


def test_unique_and_multiple_correctness():
    random.seed(23)
    task = BetweennessTripleSeriation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            mode = entry.metadata['mode']
            triples = entry.metadata['triples']
            n = entry.metadata['n']
            if mode == 'multiple':
                assert int(entry.answer) == _count_orders(n, triples)
            elif mode == 'unique':
                ans = _parse_list(entry.answer)
                assert sorted(ans) == list(range(n))
