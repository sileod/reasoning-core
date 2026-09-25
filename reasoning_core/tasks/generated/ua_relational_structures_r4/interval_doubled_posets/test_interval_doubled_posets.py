import random

import pytest

from .interval_doubled_posets import (
    IntervalDoubledPosets,
    _addr_str,
    _build_doubled,
    _covers,
)


def _labels_of(addr):
    return [_addr_str(t) for t in addr]


def test_gold_scores_one():
    t = IntervalDoubledPosets()
    for _ in range(40):
        e = t.generate_example()
        assert e.answer in ("YES", "NO")
        assert t.score_answer(e.answer, e) == 1.0


def test_bad_answers_score_zero():
    t = IntervalDoubledPosets()
    for _ in range(40):
        e = t.generate_example()
        assert t.score_answer("", e) < 1.0
        assert t.score_answer("   ", e) < 1.0
        assert t.score_answer("MAYBE", e) < 1.0
        assert t.score_answer(str(random.randint(0, 10 ** 6)), e) < 1.0


def test_answer_matches_given():
    t = IntervalDoubledPosets()
    for _ in range(60):
        e = t.generate_example()
        x, y = e.metadata["cmp"]
        assert e.answer == ("YES" if e.metadata["answer"] == "YES" else "NO")


def test_levels_generate():
    t = IntervalDoubledPosets()
    for level in (0, 1, 2, 3, 4, 5, 6):
        t.config.set_level(level)
        seen = set()
        for _ in range(30):
            e = t.generate_example()
            seen.add(e.answer)
        assert seen.issubset({"YES", "NO"})


def test_doubling_preserves_two_layer_chain():
    # A singleton interval [x,x] must become a two-element chain x0 < x1 with both
    # copies inheriting exactly the outside comparisons of x.
    addr = [(0,), (1,), (2,)]
    le = [{0, 1}, {1}, {1}]  # 0<=1, 2<=1 only
    newaddr, le2 = _build_doubled(addr, le, [1])
    labels = _labels_of(newaddr)
    # interval element 1 became (1,0) and (1,1); 0 and 2 stay.
    assert (1, 0) in newaddr and (1, 1) in newaddr
    i0 = labels.index("1.0")
    i1 = labels.index("1.1")
    assert i1 in le2[i0] and i0 not in le2[i1]
    # outside elements 0 and 2 were both <= 1, so both are <= the two copies.
    for base in ("0", "2"):
        o = labels.index(base)
        assert i0 in le2[o] and i1 in le2[o]
        # and neither copy is <= an outside element strictly above them.
        assert o not in le2[i0] and o not in le2[i1]


def test_covers_are_immediate():
    le = [{0, 1, 2, 3}, {1, 3}, {2, 3}, {3}]
    covs = _covers(le)
    covset = set(covs)
    # 1 covers 3 and 2 covers 3 (both immediate); 0 does not cover 3 (1 and 2 between).
    assert (1, 3) in covset
    assert (2, 3) in covset
    assert (0, 3) not in covset
    assert (0, 1) in covset
    assert (0, 2) in covset
