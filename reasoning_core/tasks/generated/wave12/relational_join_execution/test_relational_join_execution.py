import random

from reasoning_core.tasks.generated.wave12.relational_join_execution.relational_join_execution import (
    RelationalJoinExecution,
    _join_rows,
    _build_relation,
)


def test_scoring_gold_and_junk():
    random.seed(1718001595)
    task = RelationalJoinExecution()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("junk", ex) == 0.0


def test_all_join_types_reachable():
    random.seed(99)
    task = RelationalJoinExecution()
    seen = set()
    for _ in range(80):
        ex = task.generate_example()
        seen.add(ex.metadata["jtype"])
    assert seen == {"inner", "left", "semi", "anti"}


def test_left_join_null_semantics():
    random.seed(7)
    task = RelationalJoinExecution()
    for _ in range(30):
        ex = task.generate_example()
        if ex.metadata["jtype"] != "left":
            continue
        proj = ex.metadata["projection"]
        r_base = ex.metadata["r_cols"]
        has_r_proj = any(c in r_base for c in proj)
        # cross-check by recomputing the join
        joined = _join_rows("left", ex.metadata["L"], ex.metadata["R"])
        expected = sum(
            max(1, sum(1 for r in ex.metadata["R"] if r[0] == l[0]))
            for l in ex.metadata["L"]
        )
        assert len(joined) == expected
        # a NULL appears only where the left row had no right match and an R column is projected
        if has_r_proj:
            assert ("NULL" in ex.answer) == any(
                not any(r[0] == l[0] for r in ex.metadata["R"])
                for l, _ in joined
            )


def test_answer_rows_match_computed_join():
    random.seed(4)
    task = RelationalJoinExecution()
    for _ in range(30):
        ex = task.generate_example()
        joined = _join_rows(ex.metadata["jtype"], ex.metadata["L"], ex.metadata["R"])
        assert len(joined) == ex.metadata["answer_rows"]
        # header plus one line per join row
        lines = ex.answer.strip("\n").split("\n")
        assert len(lines) == len(joined) + 1


def test_repeated_keys_present():
    random.seed(3)
    task = RelationalJoinExecution()
    for _ in range(30):
        ex = task.generate_example()
        lk = [r[0] for r in ex.metadata["L"]]
        rk = [r[0] for r in ex.metadata["R"]]
        assert len(set(lk)) < len(lk)
        assert len(rk) > 1


def test_difficulty_changes():
    task = RelationalJoinExecution()
    task.config.set_level(0)
    c0 = task.config.n_l
    task.config.set_level(5)
    c5 = task.config.n_l
    assert c5 > c0


def test_projection_varies_and_answers_not_constant():
    random.seed(11)
    task = RelationalJoinExecution()
    projs = set()
    answers = set()
    for _ in range(40):
        ex = task.generate_example()
        projs.add(tuple(ex.metadata["projection"]))
        answers.add(ex.answer)
    assert len(projs) > 1
    assert len(answers) > 10


def test_semi_used_for_key_match_only():
    random.seed(13)
    task = RelationalJoinExecution()
    for _ in range(30):
        ex = task.generate_example()
        if ex.metadata["jtype"] != "semi":
            continue
        L = ex.metadata["L"]
        R = ex.metadata["R"]
        # semi result rows = L rows that have any key match, projected over L columns
        kept = [i for i, l in enumerate(L) if any(r[0] == l[0] for r in R)]
        proj = ex.metadata["projection"]
        l_names = ex.metadata["l_cols"]
        assert len(kept) == ex.metadata["answer_rows"]
        rows = ex.answer.strip("\n").split("\n")[1:]
        for i, rowline in zip(kept, rows):
            expect = [L[i][l_names.index(c)] for c in proj]
            assert rowline == ", ".join(str(v) for v in expect)
