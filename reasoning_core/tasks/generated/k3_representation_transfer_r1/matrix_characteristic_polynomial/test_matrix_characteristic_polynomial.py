import random

import pytest

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_representation_transfer_r1.matrix_characteristic_polynomial.matrix_characteristic_polynomial import (
    MatrixCharacteristicPolynomial,
    MatrixCharacteristicPolynomialV2Config,
    _coeffs_from_traces,
    _format_vector,
    _faddeev_leverrier,
    _matmul,
    _parse_vector,
    score_answer,
)


def test_roundtrip_scores_one():
    task = MatrixCharacteristicPolynomial()
    task.config.set_level(0)
    e = task.generate_example()
    assert score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    task = MatrixCharacteristicPolynomial()
    task.config.set_level(0)
    e = task.generate_example()
    assert score_answer("", e) == 0.0
    assert score_answer("not a vector", e) == 0.0
    assert score_answer("[1,2,abc]", e) == 0.0


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_generates_all_levels(level):
    task = MatrixCharacteristicPolynomial()
    task.config.set_level(level)
    for _ in range(10):
        e = task.generate_example()
        assert score_answer(e.answer, e) == 1.0


def test_faddeev_matches_direct():
    for _ in range(50):
        n = random.randint(2, 4)
        mat = [[random.randint(-3, 3) for _ in range(n)] for _ in range(n)]
        # symmetrize
        for i in range(n):
            for j in range(i + 1, n):
                mat[j][i] = mat[i][j]
        coeffs = _coeffs_from_traces(_faddeev_leverrier(mat, n), n)
        det = _det(mat)
        # constant term = (-1)^n * det
        expected_const = ((-1) ** n) * det
        assert coeffs[n] == expected_const
        # char poly evaluated at 0 = determinant * (-1)^n, matches; also trace
        assert coeffs[1] == -sum(mat[i][i] for i in range(n))


def _det(mat):
    n = len(mat)
    if n == 1:
        return mat[0][0]
    if n == 2:
        return mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]
    total = 0
    for c in range(n):
        sub = [[row[j] for j in range(n) if j != c] for row in mat[1:]]
        total += (-1) ** c * mat[0][c] * _det(sub)
    return total


def test_difficulty_changes_config():
    task = MatrixCharacteristicPolynomial()
    task.config.set_level(0)
    n0 = task.config.n
    task2 = MatrixCharacteristicPolynomial()
    task2.config.set_level(6)
    n6 = task2.config.n
    assert n6 >= n0


def test_matmul():
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    assert _matmul(a, b) == [[19, 22], [43, 50]]


def test_parse_format_roundtrip():
    for vec in ([1], [1, 0, -4], [-3, 2, 0, 1]):
        assert _parse_vector(_format_vector(vec)) == vec


def test_answer_not_constant_across_level():
    task = MatrixCharacteristicPolynomial()
    answers = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            answers.add(task.generate_example().answer)
    assert len(answers) > 1


def test_metadata_json_serializable():
    import json
    task = MatrixCharacteristicPolynomial()
    task.config.set_level(6)
    e = task.generate_example()
    json.dumps(e.metadata)
    assert isinstance(e.metadata["n"], int)
    assert isinstance(e.metadata["coeffs"][0], int)


def test_gold_matches_sympy():
    import sympy as sp
    task = MatrixCharacteristicPolynomial()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(10):
            e = task.generate_example()
            mat = sp.Matrix(e.metadata["matrix"])
            charpoly = list(mat.charpoly().all_coeffs())  # descending, leading first
            ascending = list(reversed(charpoly))
            assert e.metadata["coeffs"] == ascending
            assert _parse_vector(e.answer) == ascending

