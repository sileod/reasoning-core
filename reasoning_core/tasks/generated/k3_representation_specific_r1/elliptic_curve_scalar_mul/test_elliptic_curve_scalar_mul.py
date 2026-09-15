import random

from reasoning_core.tasks.generated.k3_representation_specific_r1.elliptic_curve_scalar_mul.elliptic_curve_scalar_mul import (
    EllipticCurveScalarMul,
    inv_mod,
    point_add,
    point_double,
    scalar_mul,
)


def test_gold_scores_one():
    for level in range(7):
        task = EllipticCurveScalarMul()
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    task = EllipticCurveScalarMul()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("1,2,3", entry) == 0.0
    assert task.score_answer(None, entry) == 0.0


def test_point_api():
    assert inv_mod(3, 17) == 6
    assert point_double(None, 1, 17) is None
    assert point_add(None, (1, 2), 1, 17) == (1, 2)


def test_scalar_mul_identity():
    task = EllipticCurveScalarMul()
    task.config.set_level(5)
    for _ in range(20):
        entry = task.generate_example()
        p = entry.metadata["p"]
        a = entry.metadata["a"]
        G = tuple(entry.metadata["G"])
        k = entry.metadata["k"]
        result = scalar_mul(k, G, a, p)
        assert tuple(result) == tuple(int(v) for v in entry.answer.split(","))
