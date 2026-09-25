import random

import pytest

from .scissors_congruence_obstruction import (
    ScissorsCongruenceObstruction,
    _normalize_flags,
    _reduce,
    _score_flags,
)


def _gold_checks(entry):
    assert entry.answer and set(entry.answer) <= set("YN")
    assert len(entry.answer) == entry.metadata["k"]
    for p in entry.metadata["pairs"]:
        ra = _reduce(p["edgesA"])
        rb = _reduce(p["edgesB"])
        assert ra == tuple(p["redA"])
        assert rb == tuple(p["redB"])
    return entry.metadata["pairs"]


def test_gold_consistent_with_flag():
    task = ScissorsCongruenceObstruction()
    for _ in range(200):
        e = task.generate_example()
        pairs = _gold_checks(e)
        for idx, p in enumerate(pairs):
            flag = e.answer[idx]
            if flag == "Y":
                assert p["volA"] == p["volB"]
                assert p["redA"] == p["redB"]
            else:
                assert p["redA"] != p["redB"]


def test_score_gold_and_junk():
    task = ScissorsCongruenceObstruction()
    y = task.generate_example()
    assert task.score_answer(y.answer, y) == 1.0
    assert task.score_answer("", y) < 1.0
    assert task.score_answer("reajrjrje9595!", y) < 1.0


def test_score_formats():
    assert _score_flags("y n y", "YNY") == 1.0
    assert _score_flags("Yes,No,Yes", "YNY") == 1.0
    assert _score_flags("YNY", "YNY") == 1.0
    assert _score_flags("NNY", "YNY") == 0.0
    assert _score_flags("YY", "YNY") == 0.0
    assert _score_flags("abc", "YNY") == 0.0


def test_normalize_flags():
    assert _normalize_flags("Y N Y", 3) == "YNY"
    assert _normalize_flags("yes no", 2) == "YN"
    assert _normalize_flags("yay", 3) is None
    assert _normalize_flags("", 2) is None


def test_labels_balanced():
    task = ScissorsCongruenceObstruction()
    random.seed(12345)
    n_y = 0
    total = 0
    for _ in range(400):
        e = task.generate_example()
        total += len(e.answer)
        n_y += e.answer.count("Y")
    frac = n_y / total
    assert 0.40 < frac < 0.60


def test_levels_change_config():
    task = ScissorsCongruenceObstruction()
    c0 = task.config.to_dict()
    task.config.set_level(6)
    c6 = task.config.to_dict()
    assert c0 != c6


def test_varied_number_of_pairs():
    task = ScissorsCongruenceObstruction()
    lengths = set()
    for _ in range(200):
        e = task.generate_example()
        lengths.add(len(e.answer))
    assert len(lengths) >= 2


def test_volume_equal_signals_dehn_only():
    task = ScissorsCongruenceObstruction()
    for _ in range(200):
        e = task.generate_example()
        for p in e.metadata["pairs"]:
            assert p["volA"] == p["volB"]


def test_cancelling_pair_reduces_to_zero():
    from .scissors_congruence_obstruction import _reduce
    assert _reduce([(4, 2, 1), (4, -2, -1)]) == (0, 0)


def test_score_caps_lengths_and_junk():
    task = ScissorsCongruenceObstruction()
    e = task.generate_example()
    k = len(e.answer)
    assert task.score_answer("Y" * (k + 1), e) < 1.0
    assert task.score_answer("Y" * k, e) < 1.0 if e.answer != "Y" * k else True
