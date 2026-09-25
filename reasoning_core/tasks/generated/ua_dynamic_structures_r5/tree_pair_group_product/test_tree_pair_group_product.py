import random

from reasoning_core.tasks.generated.ua_dynamic_structures_r5.tree_pair_group_product.tree_pair_group_product import (
    TreePairGroupProduct,
    _reduce,
    _INV,
)

random.seed(1662004003)


def test_reduce_cancels_inverses():
    assert _reduce("aA") == ()
    assert _reduce("AbBa") == ()
    assert _reduce("abBAc") == ("c",)


def test_reduce_is_idempotent():
    for _ in range(200):
        word = list(random.choice(["a", "A", "b", "B", "c", "C"]) for _ in range(8))
        r = _reduce(word)
        assert _reduce(r) == r


def test_gold_answer_scores_one():
    task = TreePairGroupProduct()
    for level in (0, 2, 5):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_difficulty_changes_config():
    task = TreePairGroupProduct()
    c0 = task.config.to_dict()
    task.config.set_level(4)
    c1 = task.config.to_dict()
    assert c0 != c1


def test_metadata_json_serializable():
    import json

    task = TreePairGroupProduct()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        json.dumps(dict(ex.metadata))


def test_generates_at_every_level():
    task = TreePairGroupProduct()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert ex.prompt
        assert task.score_answer(ex.answer, ex) == 1.0


def test_inverse_consistency():
    for g in "abcABC":
        assert _INV[_INV[g]] == g
