import random

from reasoning_core.tasks.generated.k3_interacting_updates_r5.binary_matrix_margin_realization.binary_matrix_margin_realization import (
    BinaryMatrixMarginRealization,
    _count_realizations,
    _score,
)


def _gen_answers(task, n, seed=99):
    import random

    random.seed(seed)
    types = {}
    for _ in range(n):
        ex = task.generate_example()
        t = ex.metadata["answer_type"]
        types[t] = types.get(t, 0) + 1
    return types


def test_unique_is_sound():
    task = BinaryMatrixMarginRealization()
    for lvl in (0, 2, 5, 6):
        cfg = task.config_cls()
        cfg.set_level(lvl)
        task.config = cfg
        n_unique = 0
        for _ in range(80):
            ex = task.generate_example()
            md = ex.metadata
            if md["answer_type"] != "unique":
                continue
            n_unique += 1
            pinmap = {(i, j): v for (i, j, v) in md["pins"]}
            cnt = _count_realizations(md["row_sums"], md["col_sums"], pinmap,
                                      md["rows"], md["cols"])
            assert cnt == 1, f"claimed unique at L{lvl} but found {cnt} realizations"
        assert n_unique > 5


def test_nonunique_has_witness():
    from reasoning_core.tasks.generated.k3_interacting_updates_r5.binary_matrix_margin_realization.binary_matrix_margin_realization import (
        _has_alternating_swap,
    )

    task = BinaryMatrixMarginRealization()
    for lvl in (0, 2, 5, 6):
        cfg = task.config_cls()
        cfg.set_level(lvl)
        task.config = cfg
        n_non = 0
        for _ in range(80):
            ex = task.generate_example()
            md = ex.metadata
            if md["answer_type"] != "non-unique":
                continue
            n_non += 1
            pinmap = {(i, j): v for (i, j, v) in md["pins"]}
            cnt = _count_realizations(md["row_sums"], md["col_sums"], pinmap,
                                      md["rows"], md["cols"])
            assert cnt > 1, f"claimed non-unique but only {cnt} realizations"
        assert n_non > 3


def test_score_semantics_nonunique_computer():
    task = BinaryMatrixMarginRealization()
    for lvl in (0, 3, 6):
        cfg = task.config_cls()
        cfg.set_level(lvl)
        task.config = cfg
        ex = task.generate_example()
        md = ex.metadata
        if task.score_answer("non-unique", ex) == 1.0:
            assert md["answer_type"] == "non-unique"
        else:
            assert md["answer_type"] == "unique"


def test_roundtrip_gold():
    task = BinaryMatrixMarginRealization()
    for _ in range(40):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_fail():
    task = BinaryMatrixMarginRealization()
    for _ in range(60):
        ex = task.generate_example()
        md = dict(ex.metadata)
        if md["answer_type"] == "non-unique":
            assert task.score_answer("unique", ex) == 0.0
            assert task.score_answer("", ex) == 0.0
            assert task.score_answer("infeasible", ex) == 0.0
        else:
            # perturb a cell
            rows = [r[:] for r in md["filling"]]
            flipped = False
            for i in range(md["rows"]):
                for j in range(md["cols"]):
                    if [i, j, rows[i][j]] not in md["pins"]:
                        rows[i][j] = 1 - rows[i][j]
                        flipped = True
                        break
                if flipped:
                    break
            assert flipped
            ans = "\n".join(" ".join(map(str, r)) for r in rows)
            assert task.score_answer(ans, ex) == 0.0


def test_label_balance():
    task = BinaryMatrixMarginRealization()
    random.seed(12345)
    types = {}
    for _ in range(200):
        ex = task.generate_example()
        t = ex.metadata["answer_type"]
        types[t] = types.get(t, 0) + 1
    assert "non-unique" in types
    assert "unique" in types
    assert types["non-unique"] > 20


def test_junk_safe():
    task = BinaryMatrixMarginRealization()
    ex = task.generate_example()
    for junk in ["", "   ", "abc", "0 1 2", "1 1\n1 1\n1"]:
        assert task.score_answer(junk, ex) < 1.0


def test_metadata_json():
    import json

    task = BinaryMatrixMarginRealization()
    ex = task.generate_example()
    json.dumps(ex.metadata)


def test_levels():
    task = BinaryMatrixMarginRealization()
    for lvl in range(7):
        cfg = task.config_cls()
        cfg.set_level(lvl)
        task.config = cfg
        for _ in range(3):
            ex = task.generate_entry()
            assert task.score_answer(ex.answer, ex) == 1.0
