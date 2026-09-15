import copy
import random

from reasoning_core.tasks.generated.wave12.btree_promoted_key.btree_promoted_key import (
    BTreePromotedKey,
    _insert_btree,
)


def _recompute(entry):
    root = copy.deepcopy(entry.metadata["root"])
    promos = _insert_btree(root, entry.metadata["order"], entry.metadata["inserted_key"])
    return promos[0] if promos else None


def test_scores_gold_all_levels():
    task = BTreePromotedKey()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            ans = task.score_answer(entry.answer, entry)
            assert ans == 1.0, (level, entry.metadata, ans)


def test_answer_domain():
    task = BTreePromotedKey()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            a = entry.metadata["answer"]
            if a is not None:
                assert isinstance(a, int)
    assert True


def test_garbage_scores_zero():
    task = BTreePromotedKey()
    task.config.set_level(2)
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("zzz", entry) < 1.0


def test_difficulty_changes_config():
    task = BTreePromotedKey()
    c0 = task.config
    c0.set_level(0)
    base = c0.min_degree
    c1 = task.config
    c1.set_level(6)
    assert c1.min_degree >= base


def test_promotion_is_valid_key():
    task = BTreePromotedKey()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_example()
            assert entry.metadata["answer"] == _recompute(entry), (
                level,
                entry.metadata,
            )


def test_reproducible_seeded():
    random.seed(1007633176)
    a = [BTreePromotedKey().generate_example().answer for _ in range(5)]
    random.seed(1007633176)
    b = [BTreePromotedKey().generate_example().answer for _ in range(5)]
    assert a == b
