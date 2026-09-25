import random

from reasoning_core.tasks.generated.ua_verification_repair_r4.pooled_distinctness_reconstruction.pooled_distinctness_reconstruction import (
    PooledDistinctnessReconstruction,
    compute_forced,
    _answer_string,
    _cached_partitions,
)


def _task_at(level):
    t = PooledDistinctnessReconstruction()
    t.config.set_level(level)
    return t


def test_gold_answer_scores_one():
    t = _task_at(3)
    e = t.generate_example()
    assert t.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    t = _task_at(3)
    e = t.generate_example()
    assert t.score_answer("", e) == 0.0
    assert t.score_answer("garbage !!!", e) == 0.0
    assert t.score_answer("[[0, 1]] and [[0]]zz", e) == 0.0


def test_answer_format_canonical():
    same = [(0, 1), (2, 3)]
    diff = [(0, 2)]
    assert _answer_string(same, diff) == "[[0, 1], [2, 3]] and [[0, 2]]"


def test_all_levels_generate_and_score():
    for level in range(7):
        t = _task_at(level)
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0
        assert e.prompt
        assert e.answer


def test_forced_is_consistent_with_hidden():
    # Every reported pool must evaluate to its stated report on the hidden_types.
    t = _task_at(4)
    e = t.generate_example()
    n = len(e.metadata['item_ids'])
    types = e.metadata['hidden_types']
    for items, kind, value in e.metadata['pools']:
        d = len({types[x] for x in items})
        if kind == '=':
            assert d == value
        elif kind == '<=':
            assert d <= value
        else:
            assert d >= value
    # Allowed: forced pairs are relations over the true hidden partition.
    true_same = {(a, b) for a in range(n) for b in range(a + 1, n) if types[a] == types[b]}
    true_diff = {(a, b) for a in range(n) for b in range(a + 1, n) if types[a] != types[b]}
    for a, b in e.metadata['forced_same']:
        assert (a, b) in true_same
    for a, b in e.metadata['forced_diff']:
        assert (a, b) in true_diff


def test_forced_matches_enumeration():
    # Recompute forced pairs by hand from metadata and confirm they agree.
    t = _task_at(3)
    e = t.generate_example()
    n = len(e.metadata['item_ids'])
    same, diff = compute_forced(n, e.metadata['pools'])
    assert list(same) == [tuple(p) for p in e.metadata['forced_same']]
    assert list(diff) == [tuple(p) for p in e.metadata['forced_diff']]


def test_always_has_nonempty_anchor():
    for level in range(7):
        t = _task_at(level)
        saw_answer = False
        for _ in range(20):
            e = t.generate_example()
            if e.answer != "[] and []":
                saw_answer = True
                break
        assert saw_answer, f"level {level}: all answers were empty"


def test_deterministic_under_seed():
    flat1 = []
    random.seed(12345)
    t = _task_at(1)
    for _ in range(5):
        flat1.append(t.generate_example().answer)
    flat2 = []
    random.seed(12345)
    t2 = _task_at(1)
    for _ in range(5):
        flat2.append(t2.generate_example().answer)
    assert flat1 == flat2


def test_partitions_reproducible():
    p1 = _cached_partitions(5)
    p2 = _cached_partitions(5)
    assert p1 == p2
