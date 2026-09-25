from sympy import Matrix

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.oriented_matroid_dual_recovery.oriented_matroid_dual_recovery import (
    OrientedMatroidDualRecovery,
    _canonical_circuit,
    _is_minimal_dependence,
)


def test_roundtrip():
    task = OrientedMatroidDualRecovery()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0


def test_junk_and_empty():
    task = OrientedMatroidDualRecovery()
    task.config.set_level(0)
    e = task.generate_example()
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("not an answer", e) == 0.0
    assert task.score_answer("1;2;3", e) == 0.0


def test_wrong_values():
    task = OrientedMatroidDualRecovery()
    task.config.set_level(0)
    e = task.generate_example()
    ans = [int(x) for x in e.answer.split(",")]
    wrong = ",".join(str(a + 1) for a in ans)
    assert task.score_answer(wrong, e) == 0.0


def test_answer_matches_nullspace():
    task = OrientedMatroidDualRecovery()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(30):
            e = task.generate_example()
            md = e.metadata
            cols = [md["columns"][j] for j in md["support"]]
            iv = _canonical_circuit(cols)
            full = [0] * md["n"]
            for pos, j in enumerate(md["support"]):
                full[j] = iv[pos]
            got = [full[j] for j in md["query"]]
            assert got == md["answers"]
            expected = ",".join(str(a) for a in got)
            assert task.score_answer(expected, e) == 1.0
            # independence: the columns sum in the relation
            sv = [iv[pos] for pos in range(len(cols))]
            A = Matrix.hstack(*[Matrix(c) for c in cols])
            prod = A * Matrix(sv)
            assert all(x == 0 for x in prod)


def test_support_minimal():
    task = OrientedMatroidDualRecovery()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(30):
            e = task.generate_example()
            md = e.metadata
            cols = [md["columns"][j] for j in md["support"]]
            assert _is_minimal_dependence(cols)
            for j in md["support"]:
                assert md["answers"][md["query"].index(j)] != 0
            for l in md["loops"]:
                assert md["answers"][md["query"].index(l)] == 0


def test_loop_values_zero():
    task = OrientedMatroidDualRecovery()
    task.config.set_level(6)
    seen_loop = False
    for _ in range(60):
        e = task.generate_example()
        if e.metadata["loops"]:
            seen_loop = True
            assert e.metadata["answers"][e.metadata["query"].index(e.metadata["loops"][0])] == 0
    assert seen_loop


def test_difficulty_monotonic():
    task = OrientedMatroidDualRecovery()
    task.config.set_level(0)
    r0, n0 = task.config.r, task.config.n
    task.config.set_level(6)
    r6, n6 = task.config.r, task.config.n
    assert n6 > n0
    assert r6 >= r0
