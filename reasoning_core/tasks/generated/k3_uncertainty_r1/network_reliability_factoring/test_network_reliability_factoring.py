import random
from fractions import Fraction

from reasoning_core.tasks.generated.k3_uncertainty_r1.network_reliability_factoring.network_reliability_factoring import (
    NetworkReliabilityFactoring,
    _bruteforce,
    _connects,
    _reliability,
)


def test_bruteforce_matches_score():
    task = NetworkReliabilityFactoring()
    for _ in range(50):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_gold_is_bruteforce_small():
    task = NetworkReliabilityFactoring()
    for _ in range(30):
        entry = task.generate_example()
        edges = {k: tuple(v) for k, v in entry.metadata["edges"].items()}
        if len(edges) <= 12:
            p = {k: Fraction(v) for k, v in entry.metadata["p"].items()}
            gold = _bruteforce(edges, p, entry.metadata["src"], entry.metadata["snk"])
            assert Fraction(entry.metadata["gold_num"], entry.metadata["gold_den"]) == gold


def test_factoring_matches_bruteforce():
    task = NetworkReliabilityFactoring()
    for _ in range(60):
        entry = task.generate_example()
        edges = {k: tuple(v) for k, v in entry.metadata["edges"].items()}
        if len(edges) <= 12:
            p = {k: Fraction(v) for k, v in entry.metadata["p"].items()}
            src, snk = entry.metadata["src"], entry.metadata["snk"]
            assert _reliability(edges, p, src, snk) == _bruteforce(edges, p, src, snk)


def test_junk_scores_zero():
    task = NetworkReliabilityFactoring()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0
    assert task.score_answer("1/0", entry) == 0.0


def test_reduced_fraction():
    task = NetworkReliabilityFactoring()
    for _ in range(30):
        entry = task.generate_example()
        val = Fraction(entry.metadata["gold_num"], entry.metadata["gold_den"])
        assert val.numerator == entry.metadata["gold_num"]
        assert val.denominator == entry.metadata["gold_den"]


def test_levels_generate():
    for level in range(7):
        task = NetworkReliabilityFactoring()
        task.config.set_level(level)
        entry = task.generate_example()
        assert entry.answer


def test_range():
    task = NetworkReliabilityFactoring()
    for _ in range(30):
        entry = task.generate_example()
        val = Fraction(entry.metadata["gold_num"], entry.metadata["gold_den"])
        assert Fraction(0) < val < Fraction(1)


def test_connects():
    assert _connects([("a", "b"), ("b", "c")], "a", "c")
    assert not _connects([("a", "b")], "a", "c")


def test_score_whitespace_and_unreduced():
    task = NetworkReliabilityFactoring()
    for _ in range(20):
        entry = task.generate_example()
        num = entry.metadata["gold_num"]
        den = entry.metadata["gold_den"]
        assert task.score_answer(f"  {num} / {den} ", entry) == 1.0
        assert task.score_answer(f"{num * 2}/{den * 2}", entry) == 1.0
        assert task.score_answer(f"{num + 1}/{den}", entry) == 0.0


def test_factoring_deterministic():
    task = NetworkReliabilityFactoring()
    for _ in range(20):
        entry = task.generate_example()
        edges = {k: tuple(v) for k, v in entry.metadata["edges"].items()}
        p = {k: Fraction(v) for k, v in entry.metadata["p"].items()}
        src, snk = entry.metadata["src"], entry.metadata["snk"]
        assert _reliability(edges, p, src, snk) == _reliability(edges, p, src, snk)


def test_series_parallel_bridge():
    edges = {"a": ("s", "x"), "b": ("x", "y"), "c": ("y", "t"), "d": ("s", "t")}
    p = {"a": Fraction(1, 2), "b": Fraction(1, 2), "c": Fraction(1, 2), "d": Fraction(1, 2)}
    assert _reliability(edges, p, "s", "t") == _bruteforce(edges, p, "s", "t")
