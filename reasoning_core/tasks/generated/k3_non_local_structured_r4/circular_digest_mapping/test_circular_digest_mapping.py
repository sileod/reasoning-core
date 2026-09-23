import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_non_local_structured_r4.circular_digest_mapping.circular_digest_mapping import (
    CircularDigestConfig,
    CircularDigestMapping,
    _cyclic_gaps,
)


def test_roundtrip_scores_one():
    task = CircularDigestMapping()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_config_level_changes_size():
    cfg = CircularDigestConfig()
    cfg.set_level(0)
    l0 = (cfg.a, cfg.b, cfg.length)
    cfg.set_level(6)
    l6 = (cfg.a, cfg.b, cfg.length)
    assert l6[2] > l0[2]
    assert l6[0] >= l0[0]


def test_answer_matches_explicit_computation():
    task = CircularDigestMapping()
    x = task.generate_example()
    md = x.metadata
    L = md["length"]
    a = md["a_fragments"]
    b = md["b_fragments"]
    ab = md["ab_fragments"]
    aco = md["a_coords"]
    bco = md["b_coords"]
    k = md["a_index"]
    m = md["b_index"]
    assert sum(a) == L
    assert sum(b) == L
    assert sum(ab) == L
    assert len(aco) == len(a) and len(bco) == len(b)
    assert all(v > 0 for v in a) and all(v > 0 for v in b)
    assert all(v > 0 for v in ab)
    assert aco[0] == 0
    gold = (bco[m] - aco[k]) % L
    assert int(x.answer) == gold
    assert 0 < int(x.answer) < L


def test_empty_and_junk_do_not_score():
    task = CircularDigestMapping()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("not a number", x) < 1.0


def test_dup_key_stable():
    task = CircularDigestMapping()
    x1 = task.generate_example()
    assert task.deduplication_key(x1) == task.deduplication_key(x1)


def test_metadata_json_serializable():
    import json

    task = CircularDigestMapping()
    x = task.generate_example()
    json.dumps(x.metadata)


def test_generate_many_levels():
    for level in (0, 3, 6):
        task = CircularDigestMapping()
        task.config.set_level(level)
        for _ in range(5):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_cyclic_gaps_roundtrip():
    points = [2, 7, 11]
    gaps = _cyclic_gaps(points, 15)
    assert gaps == [5, 4, 6]
