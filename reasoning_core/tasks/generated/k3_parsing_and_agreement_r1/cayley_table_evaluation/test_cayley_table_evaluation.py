import json
import random

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.cayley_table_evaluation.cayley_table_evaluation import (
    CayleyTableEvaluation,
    _eval,
)

random.seed(0)


def _gen(level):
    task = CayleyTableEvaluation()
    task.config.set_level(level)
    return task.generate_example()


def test_round_trip_mode1():
    task = CayleyTableEvaluation()
    for level in range(7):
        task.config.set_level(level)
        got = None
        while got is None:
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1
            if x.metadata.mode == 1:
                got = x
        assert len(got.metadata.table) == got.metadata.n
        assert got.answer.isdigit()


def test_round_trip_mode2():
    task = CayleyTableEvaluation()
    for level in range(7):
        task.config.set_level(level)
        got = None
        while got is None:
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1
            if x.metadata.mode == 2:
                got = x
        assert 0 <= got.metadata.rhs < got.metadata.n
        assert got.answer.isdigit()


def test_round_trip_mode3():
    task = CayleyTableEvaluation()
    for level in range(7):
        task.config.set_level(level)
        got = None
        while got is None:
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1
            if x.metadata.mode == 3:
                got = x
        i, a = got.answer.split(";")
        assert i.isdigit() and a.isdigit()


def test_all_modes_occur():
    task = CayleyTableEvaluation()
    modes = set()
    for _ in range(400):
        x = task.generate_example()
        modes.add(x.metadata.mode)
    assert modes == {1, 2, 3}


def test_metadata_json_serializable():
    task = CayleyTableEvaluation()
    for level in (0, 6):
        task.config.set_level(level)
        x = task.generate_example()
        json.dumps(dict(x.metadata))


def test_score_rejects_junk():
    task = CayleyTableEvaluation()
    x = task.generate_example()
    assert task.score_answer("garbage", x) == 0
    assert task.score_answer("", x) == 0


def test_mode2_unique_solution():
    task = CayleyTableEvaluation()
    for _ in range(80):
        x = task.generate_example()
        if x.metadata.mode == 2:
            sols = [v for v in range(x.metadata.n)
                    if _eval(x.metadata.expr, x.metadata.table, v) == x.metadata.rhs]
            assert sols == [int(x.answer)]


def test_mode2_variable_occurs_multiple_times():
    from itertools import product

    task = CayleyTableEvaluation()
    for _ in range(80):
        x = task.generate_example()
        if x.metadata.mode == 2:
            expr = x.metadata.expr
            # count variable leaves ("v" leaf nodes)
            count = [0]

            def walk(e):
                if e[0] == "v":
                    count[0] += 1
                elif e[0] == "o":
                    walk(e[1])
                    walk(e[2])

            walk(expr)
            assert count[0] >= 2


def test_mode3_unique_identity_absorbing():
    task = CayleyTableEvaluation()
    for _ in range(80):
        x = task.generate_example()
        if x.metadata.mode == 3:
            n = x.metadata.n
            i, a = (int(v) for v in x.answer.split(";"))
            assert i != a
            t = x.metadata.table
            assert all(t[i][j] == j and t[j][i] == j for j in range(n))
            assert all(t[a][j] == a and t[j][a] == a for j in range(n))
