import random

from reasoning_core.template import Entry, Reward
from reasoning_core.tasks.generated.k3_representation_transfer_r1.floor_quotient_blocks.floor_quotient_blocks import (
    FloorQuotientBlocks,
    FloorQuotientBlocksConfig,
    _block_span,
)


def _task(level=0):
    task = FloorQuotientBlocks(config=FloorQuotientBlocksConfig())
    task.config.set_level(level)
    return task


def test_gold_answer_scores_one():
    task = _task()
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_rejects_garbage():
    task = _task()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0
    assert task.score_answer("12", ex) == 0.0
    assert task.score_answer("1 2 3", ex) == 0.0
    assert task.score_answer("X Y", ex) == 0.0


def test_score_rejects_wrong_block():
    task = _task()
    ex = task.generate_example()
    s, e = ex.metadata["start"], ex.metadata["end"]
    assert task.score_answer(f"{s} {e + 1}", ex) == 0.0
    assert task.score_answer(f"{s - 1} {e}", ex) == 0.0


def test_block_span_is_exact_maximal():
    task = _task(level=6)
    for _ in range(30):
        ex = task.generate_example()
        n, i = ex.metadata["n"], ex.metadata["i"]
        q = n // i
        s, e = ex.metadata["start"], ex.metadata["end"]
        # every k in the block has the queried quotient
        assert all(n // k == q for k in range(s, e + 1))
        # the block is maximal
        if s > 1:
            assert n // (s - 1) != q
        if e < n:
            assert n // (e + 1) != q


def test_block_span_matches_bruteforce():
    for n in range(2, 200):
        for i in range(1, n + 1):
            q = n // i
            ks = [k for k in range(1, n + 1) if n // k == q]
            assert _block_span(n, i) == (min(ks), max(ks))
            assert (min(ks), max(ks)) == (min(ks), max(ks))


def test_difficulty_increases():
    t0 = _task(0)
    t6 = _task(6)
    assert t6.config.max_n > t0.config.max_n


def test_deterministic_under_seed():
    random.seed(123)
    t1 = _task(3)
    a1 = [t1.generate_example().answer for _ in range(5)]
    random.seed(123)
    t2 = _task(3)
    a2 = [t2.generate_example().answer for _ in range(5)]
    assert a1 == a2


def test_metadata_json_serializable():
    import json
    task = _task(5)
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))
