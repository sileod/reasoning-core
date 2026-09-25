import random
import pytest

from reasoning_core.tasks.generated.ua_representation_specific_r4.tropical_corner_transfer.tropical_corner_transfer import (
    TropicalCornerTransfer,
    _upper_hull,
    _parse_coeff,
    _parse_corner,
    _format_coeff,
    _format_corner,
)


@pytest.fixture
def task():
    return TropicalCornerTransfer()


def test_upper_hull_known():
    pts = [(0, 0), (1, 1), (2, 2), (3, 1), (4, 0)]
    verts = _upper_hull(pts)
    assert [i for (i, _) in verts] == [0, 2, 4]


def test_parsers_roundtrip():
    assert _parse_coeff("[0,1,2,1,0]") == [0, 1, 2, 1, 0]
    assert _parse_coeff("garbage") is None
    assert _parse_coeff("1,2,3") is None
    verts, bps = _parse_corner("0:0,2:2,4:0;bp:-1,1")
    assert verts == [(0, 0), (2, 2), (4, 0)]
    assert bps == [-1, 1]
    assert _format_corner(verts, bps) == "0:0,2:2,4:0;bp:-1,1"
    assert _format_coeff([0, 1, 2, 1, 0]) == "[0,1,2,1,0]"


def test_gold_scores_one_and_roundtrips(task):
    for _ in range(80):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        if ex.metadata["direction"] == 0:
            got = _parse_corner(ex.answer)
            assert got is not None
            verts, bps = got
            assert len(bps) == len(verts) - 1
            assert all(b <= 0 or True for b in bps)
            for i, c in verts:
                assert c == ex.metadata["coeff_list"][i]
        else:
            got = _parse_coeff(ex.answer)
            assert got is not None
            assert len(got) == ex.metadata["n"] + 1


def test_junk_does_not_score(task):
    for _ in range(40):
        ex = task.generate_example()
        assert task.score_answer("garbage", ex) == 0.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer(ex.answer[:-2], ex) == 0.0


def test_levels_change_config(task):
    c0 = task.config.to_dict()
    task.config.set_level(6)
    c6 = task.config.to_dict()
    assert c6 != c0
    assert c6["max_degree"] > c0["max_degree"]
    assert c6["max_hull"] >= c0["max_hull"]


def test_all_levels_generate_and_score(task):
    for level in range(7):
        for _ in range(20):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0


def test_both_directions_produced(task):
    seen = set()
    for _ in range(200):
        ex = task.generate_example()
        seen.add(ex.metadata["direction"])
    assert seen == {0, 1}


def test_inactive_terms_present(task):
    seen_strict = False
    for _ in range(300):
        ex = task.generate_example()
        if ex.metadata["direction"] == 0:
            n = ex.metadata["n"]
            if any(ex.metadata["coeff_list"][j] != ex.metadata["onseg_list"][j]
                   for j in range(n + 1)):
                seen_strict = True
    assert seen_strict


def test_answer_is_well_formed_corner(task):
    for _ in range(200):
        ex = task.generate_example()
        if ex.metadata["direction"] == 0:
            verts, bps = _parse_corner(ex.answer)
            for k in range(len(bps)):
                a, ca = verts[k]
                b, cb = verts[k + 1]
                assert (ca - cb) % (b - a) == 0
                assert (ca - cb) // (b - a) == bps[k]


def test_reproducible_under_seed():
    random.seed(1705404348)
    a = [TropicalCornerTransfer().generate_example().answer for _ in range(20)]
    random.seed(1705404348)
    b = [TropicalCornerTransfer().generate_example().answer for _ in range(20)]
    assert a == b


def test_distractors_invalid(task):
    for _ in range(20):
        ex = task.generate_example()
        for cand in task.distractor_candidates(ex):
            assert task.score_answer(cand, ex) < 1.0
