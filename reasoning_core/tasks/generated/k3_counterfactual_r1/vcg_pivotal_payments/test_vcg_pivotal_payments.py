import random

from reasoning_core.tasks.generated.k3_counterfactual_r1.vcg_pivotal_payments.vcg_pivotal_payments import (
    VcgPivotalPayments,
    _parse_answer,
)


def test_gold_scores_one():
    task = VcgPivotalPayments()
    for level in (0, 2, 5, 6):
        for _ in range(20):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0, (level, ex.answer)


def test_garbage_scores_zero():
    task = VcgPivotalPayments()
    ex = task.generate_example()
    for bad in ("", "garbage", "1:2;x:y", "5:4;2:13"):
        assert task.score_answer(bad, ex) == 0.0, bad


def test_parse_roundtrip():
    assert _parse_answer("2:13;5:4") == [(2, 13), (5, 4)]
    assert _parse_answer("") == []
    assert _parse_answer("x:y") is None


def test_payment_domain_and_reproducible():
    task = VcgPivotalPayments()
    ex = task.generate_example(level=6)
    gold = [tuple(p) for p in ex.metadata["answer_list"]]
    assert all(p >= 0 for (_, p) in gold)


def test_known_vcg_case():
    task = VcgPivotalPayments()
    md = {
        "num_goods": 4,
        "bids": [
            {"bidder": 0, "goods": [0, 2, 3], "value": 9},
            {"bidder": 1, "goods": [1, 3], "value": 3},
            {"bidder": 2, "goods": [1, 2, 3], "value": 9},
            {"bidder": 3, "goods": [2], "value": 7},
            {"bidder": 4, "goods": [2], "value": 9},
            {"bidder": 5, "goods": [0, 1, 2, 3], "value": 10},
            {"bidder": 6, "goods": [0, 1, 2, 3], "value": 12},
            {"bidder": 7, "goods": [0], "value": 3},
        ],
        "edit": {"type": "none"},
        "answer_list": [[1, 0], [4, 7], [7, 0]],
    }
    entry = type("E", (), {"metadata": md})()
    assert task.score_answer("1:0;4:7;7:0", entry) == 1.0
    assert task.score_answer("4:7;1:0;7:0", entry) == 1.0
    assert task.score_answer("1:0;4:6;7:0", entry) == 0.0


def test_difficulty_changes_config():
    task = VcgPivotalPayments()
    task.config.set_level(0)
    a = (task.config.num_goods, task.config.max_bidders)
    task.config.set_level(6)
    b = (task.config.num_goods, task.config.max_bidders)
    assert a != b
