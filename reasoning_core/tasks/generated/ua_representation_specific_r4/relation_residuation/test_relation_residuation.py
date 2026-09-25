import random

from reasoning_core.tasks.generated.ua_representation_specific_r4.relation_residuation.relation_residuation import (
    RelationResiduation,
)


def _residual(side, G, T, rows, cols):
    if side == "right":
        X = set()
        for j in range(cols):
            for k in range(cols):
                if all((i, k) in T for i in range(rows) if (i, j) in G):
                    X.add((j, k))
    else:
        X = set()
        for i in range(rows):
            for m in range(rows):
                if all((i, k) in T for k in range(cols) if (m, k) in G):
                    X.add((i, m))
    return sorted(X)


def _compose_left(G, X, rows, cols):
    # G ; X over shared cols
    out = set()
    for (i, j) in G:
        for (j2, k) in X:
            if j2 == j:
                out.add((i, k))
    return out


def _compose_right(X, G, rows, cols):
    # X ; G : X (rows x rows), G (rows x cols) over shared rows
    out = set()
    for (i, m) in X:
        for (m2, k) in G:
            if m2 == m:
                out.add((i, k))
    return out


def test_gold_membership_scores():
    task = RelationResiduation()
    random.seed(1339177894)
    for _ in range(300):
        e = task.generate_example()
        if e.metadata["answer_mode"] == "membership":
            assert task.score_answer(e.answer, e) == 1.0
            assert task.score_answer(e.answer, e) == 1.0


def test_gold_relation_scores():
    task = RelationResiduation()
    random.seed(42)
    for _ in range(300):
        e = task.generate_example()
        if e.metadata["answer_mode"] == "relation":
            assert task.score_answer(e.answer, e) == 1.0
            assert task.score_answer("garbage!!", e) < 1.0


def test_answers_domain():
    task = RelationResiduation()
    random.seed(7)
    for _ in range(500):
        e = task.generate_example()
        p = e.metadata["payload"]
        rows, cols = p["rows"], p["cols"]
        G = set(map(tuple, p["G"]))
        T = set(map(tuple, p["T"]))
        assert all(0 <= a < rows and 0 <= b < cols for (a, b) in G | T)
        X = set(map(tuple, p["X"]))
        if p["side"] == "right":
            comp = _compose_left(G, X, rows, cols)
        else:
            comp = _compose_right(X, G, rows, cols)
        assert comp.issubset(T)
        # largest: recompute residual independently
        gold = _residual(p["side"], G, T, rows, cols)
        assert sorted(X) == gold


def test_largest_property():
    from reasoning_core.tasks.generated.ua_representation_specific_r4.relation_residuation.relation_residuation import (
        _compose,
    )

    task = RelationResiduation()
    random.seed(99)
    for _ in range(300):
        e = task.generate_example()
        p = e.metadata["payload"]
        rows, cols = p["rows"], p["cols"]
        G = set(map(tuple, p["G"]))
        T = set(map(tuple, p["T"]))
        assert _residual(p["side"], G, T, rows, cols) == sorted(set(map(tuple, p["X"])))
