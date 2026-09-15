import random

import pytest

from reasoning_core.tasks.generated.k3_representation_specific_r1.matrix_jordan_normal_form.matrix_jordan_normal_form import (
    MatrixJordan,
    MatrixJordanConfig,
    _char_poly,
    _factor_char_poly,
    _jordan_data,
    _mat_mul,
    _mat_pow,
    _rank,
)


def _identity(n):
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def _mul(A, B, p):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) % p for j in range(n)] for i in range(n)]


def _det(M, p):
    n = len(M)
    a = [row[:] for row in M]
    det = 1
    for i in range(n):
        if a[i][i] % p == 0:
            for j in range(i + 1, n):
                if a[j][i] % p != 0:
                    a[i], a[j] = a[j], a[i]
                    det = (-det) % p
                    break
        if a[i][i] % p == 0:
            return 0
        piv = a[i][i] % p
        det = det * piv % p
        inv = pow(piv, p - 2, p)
        for j in range(i + 1, n):
            fac = a[j][i] % p
            if fac:
                for k in range(i, n):
                    a[j][k] = (a[j][k] - fac * inv * a[i][k]) % p
    return det % p


def test_roundtrip_every_level():
    for level in range(7):
        cfg = MatrixJordanConfig()
        cfg.set_level(level)
        task = MatrixJordan()
        task.config = cfg
        for _ in range(30):
            entry = task.generate_entry()
            assert task.score_answer(entry.answer, entry) == 1.0
            assert entry.answer == entry.metadata["answer"]


def test_char_poly_matches_determinant():
    # char poly = det(xI - A)
    import random

    for p in (5, 7, 11, 13):
        n = 3
        for _ in range(20):
            m = [[random.randrange(p) for _ in range(n)] for _ in range(n)]
            coefs = _char_poly(m, p)
            # evaluate the polynomial at a few x against det(xI - A)
            for x in (0, 1, 2):
                Mx = [[((x if i == j else 0) - m[i][j]) % p for j in range(n)] for i in range(n)]
                d = _det(Mx, p)
                val = 0
                for c in reversed(coefs):
                    val = (val * x + c) % p
                assert val == d


def test_jordan_data_matches_builtin_structure():
    # a matrix built with given jordan blocks must reproduce those blocks
    import random

    for _ in range(30):
        n = random.randint(2, 4)
        p = random.choice([q for q in (5, 7, 11, 13) if q > n])
        # choose eigenvalues with multiplicities partitioning n
        num_eig = random.randint(1, n)
        mults = [1] * num_eig
        for _ in range(n - num_eig):
            mults[random.randrange(num_eig)] += 1
        eigs = sorted(random.sample(range(1, p), num_eig))
        parts = []
        matrix = [[0] * n for _ in range(n)]
        off = 0
        for eig, mult in zip(eigs, mults):
            inner = []
            rem = mult
            while rem > 0:
                b = random.randint(1, rem)
                inner.append(b)
                rem -= b
            inner.sort(reverse=True)
            for b in inner:
                for i in range(b):
                    matrix[off + i][off + i] = eig
                for i in range(b - 1):
                    matrix[off + i][off + i + 1] = 1
                off += b
            parts.append(f"eig={eig}:blk={inner}")
        canonical = ";".join(parts)
        computed = _jordan_data(matrix, p)
        assert computed == canonical


def test_score_junk():
    cfg = MatrixJordanConfig()
    cfg.set_level(0)
    task = MatrixJordan()
    task.config = cfg
    entry = task.generate_entry()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0
    assert task.score_answer(entry.answer + " ", entry) == 1.0
    assert task.score_answer(None, entry) == 0.0


def test_metadata_json_serializable():
    import json

    for level in (0, 3, 6):
        cfg = MatrixJordanConfig()
        cfg.set_level(level)
        task = MatrixJordan()
        task.config = cfg
        for _ in range(10):
            entry = task.generate_entry()
            json.dumps(entry.metadata)
