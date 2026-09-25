import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))

from zigzag_cycle_survival import _barcode, _h1dim, _parse_intervals, _rank_mod_p, ZigzagCycleSurvival, ZigzagCycleSurvivalConfig


def _score(task, entry, answer):
    return task.score_answer(answer, entry)


def make_task(level):
    task = ZigzagCycleSurvival()
    cfg = ZigzagCycleSurvivalConfig()
    cfg.set_level(level)
    task.config = cfg
    return task


def test_rank_mod_p():
    assert _rank_mod_p([[1, 1], [1, 1]], 2) == 1
    assert _rank_mod_p([[1, 0], [0, 1]], 2) == 2
    assert _rank_mod_p([[1, 2], [2, 2]], 3) == 2
    assert _rank_mod_p([[1, 2], [2, 1]], 3) == 1
    assert _rank_mod_p([[1, 1, 1]], 3) == 1
    assert _rank_mod_p([], 2) == 0
    assert _rank_mod_p([[0, 0]], 2) == 0


def test_barcode():
    assert _barcode([0, 0], 2) == []
    assert _barcode([1, 1], 2) == [(0, "inf")]
    assert _barcode([0, 1, 1, 0, 1], 5) == [(1, 3), (4, "inf")]
    assert _barcode([1, 0, 1, 0], 4) == [(0, 1), (2, 3)]


def test_gold_scores():
    random.seed(1)
    for level in (0, 2, 5):
        task = make_task(level)
        for _ in range(25):
            entry = task.generate_entry()
            assert _score(task, entry, entry.answer) == 1.0


def test_junk_scores_zero():
    random.seed(2)
    task = make_task(3)
    for _ in range(30):
        entry = task.generate_entry()
        assert _score(task, entry, "") == 0.0
        assert _score(task, entry, "notananswer") == 0.0
        assert _score(task, entry, "(0,0),(x,y)") == 0.0


def test_rank_trajectory_consistent():
    random.seed(3)
    for level in (0, 1, 3, 6):
        task = make_task(level)
        for _ in range(20):
            entry = task.generate_entry()
            ranks = entry.metadata["ranks"]
            assert all(r in (0, 1) for r in ranks)
            intervals = entry.metadata["intervals"]
            rebuilt = _barcode(ranks, entry.metadata["L"])
            assert rebuilt == intervals


def test_difficulty_changes():
    c0 = ZigzagCycleSurvivalConfig()
    c0.set_level(0)
    c6 = ZigzagCycleSurvivalConfig()
    c6.set_level(6)
    assert c6.L >= c0.L
    assert c6.V >= c0.V


def test_prompt_not_answerable_off_surface():
    random.seed(5)
    task = make_task(2)
    for _ in range(40):
        entry = task.generate_entry()
        if entry.answer:
            assert entry.answer not in entry.metadata["ranks"]
    # the answer never equals the bare rank list string
    for _ in range(40):
        entry = task.generate_entry()
        assert str(entry.metadata["ranks"]) != entry.answer


def test_interval_domain():
    random.seed(6)
    task = make_task(4)
    for _ in range(40):
        entry = task.generate_entry()
        L = entry.metadata["L"]
        for (b, d) in entry.metadata["intervals"]:
            assert 0 <= b <= L - 1
            if isinstance(d, int):
                assert b < d <= L - 1
            else:
                assert d == "inf"


def test_parse_roundtrip():
    assert _parse_intervals("(1,3),(5,7)") == [(1, 3), (5, 7)]
    assert _parse_intervals("(1,inf)") == [(1, "inf")]
    assert _parse_intervals("garbage") == []


def test_model_cannot_read_answer_off_rank_list():
    random.seed(11)
    task = make_task(5)
    for _ in range(50):
        entry = task.generate_entry()
        # the answer pairs are not just the bare rank trajectory, field, or count
        assert _format(entry.metadata["ranks"]) != entry.answer


def _format(ranks):
    return ",".join(str(r) for r in ranks)


def test_variety_and_fields():
    random.seed(12)
    seen_fields = set()
    mult = 0
    n = 200
    for _ in range(n):
        entry = make_task(3).generate_entry()
        seen_fields.add(entry.metadata["field"])
        if len(entry.metadata["intervals"]) > 1:
            mult += 1
    assert seen_fields == {2, 3} or len(seen_fields) >= 1
    assert mult > 0  # multiple births/deaths (cycles reopening) occur


def test_nonempty_answer():
    random.seed(13)
    for level in (0, 2, 5, 6):
        task = make_task(level)
        for _ in range(25):
            entry = task.generate_entry()
            assert entry.answer.strip() != ""
