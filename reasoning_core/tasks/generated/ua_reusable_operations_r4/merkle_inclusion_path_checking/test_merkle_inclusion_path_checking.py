import random

from reasoning_core.tasks.generated.ua_reusable_operations_r4.merkle_inclusion_path_checking.merkle_inclusion_path_checking import (
    MerkleInclusionPathChecking,
    _BASE,
    _combine,
)

TASK = MerkleInclusionPathChecking


def _fold(leaf, sides, siblings, modulus):
    cur = leaf
    for side, sibling in zip(sides, siblings):
        cur = _combine(cur, sibling, side, modulus)
    return cur


def test_gold_scores_one():
    task = TASK()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_matches_fold():
    task = TASK()
    random.seed(798610012)
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_entry()
            md = ex.metadata
            leaf = md["leaf"]
            sides = [lvl["side"] for lvl in md["levels"]]
            siblings = [lvl["sibling"] for lvl in md["levels"]]
            mod = md["modulus"]
            assert _fold(leaf, sides, siblings, mod) == md["root"]
            status = md["status"]
            stated = [lvl["stated"] for lvl in md["levels"]]
            assert ex.answer == f"{md['root']}|{status}"


def test_first_mismatch_correct():
    task = TASK()
    random.seed(11)
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_entry()
            md = ex.metadata
            cur = md["leaf"]
            mism = None
            for i, lvl in enumerate(md["levels"], start=1):
                cur = _combine(cur, lvl["sibling"], lvl["side"], md["modulus"])
                if mism is None and cur != lvl["stated"]:
                    mism = i
            expected = "valid" if mism is None else str(mism)
            assert md["status"] == expected


def test_valid_and_corrupt_both_reachable():
    task = TASK()
    random.seed(3)
    seen = set()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(200):
            ex = task.generate_entry()
            seen.add(ex.metadata["status"])
    assert "valid" in seen
    assert any(s != "valid" for s in seen)


def test_junk_and_empty_do_not_score():
    task = TASK()
    random.seed(7)
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer("", ex) == 0.0
            assert task.score_answer("reajrjrje9595!", ex) == 0.0
            assert task.score_answer(" ", ex) == 0.0


def test_level_changes_config():
    task = TASK()
    base = task.config.max_levels
    task.config.set_level(3)
    assert task.config.max_levels != base


def test_combine_side_symmetric_when_equal():
    mod = 101
    assert _combine(5, 7, "L", mod) == (5 * _BASE + 7) % mod
    assert _combine(5, 7, "R", mod) == (7 * _BASE + 5) % mod
