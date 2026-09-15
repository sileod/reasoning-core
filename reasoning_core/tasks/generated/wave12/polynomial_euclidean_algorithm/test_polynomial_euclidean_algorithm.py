import random

from reasoning_core.tasks.generated.wave12.polynomial_euclidean_algorithm.polynomial_euclidean_algorithm import (
    PolynomialEuclideanAlgorithm,
    _poly_mod,
    _gcd,
    _monic,
    _trim,
)


def _check_instance(task, level):
    task.config.set_level(level)
    ex = task.generate_example()
    ans = ex.answer.split(",")
    assert len(ans) == ex.metadata["max_degree"] + 1
    assert all(a.isdigit() for a in ans)
    assert task.score_answer(ex.answer, ex) == 1.0


def test_roundtrip_gold_scores_one_across_levels():
    task = PolynomialEuclideanAlgorithm()
    for level in (0, 1, 2, 3, 4, 5):
        _check_instance(task, level)


def test_wrong_and_junk_answers_rejected():
    task = PolynomialEuclideanAlgorithm()
    task.config.set_level(2)
    ex = task.generate_example()
    assert task.score_answer("0,0,0", ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0


def test_reference_gcd_helper_monic_and_consistent():
    a = [1, 0, 2, 3]
    b = [1, 4, 0]
    g = _gcd(list(a), list(b))
    assert _monic(list(g)) == list(g)
    assert _trim(_poly_mod(list(a), list(g))) == []
    assert _trim(_poly_mod(list(b), list(g))) == []


def test_deterministic_under_seed():
    random.seed(7)
    t1 = PolynomialEuclideanAlgorithm()
    t1.config.set_level(3)
    e1 = t1.generate_example()

    random.seed(7)
    t2 = PolynomialEuclideanAlgorithm()
    t2.config.set_level(3)
    e2 = t2.generate_example()

    assert e1.answer == e2.answer
    assert list(e1.metadata["a_high"]) == list(e2.metadata["a_high"])
