import json

from reasoning_core.tasks.generated.k3_synthetic_grammars_r4.word_equation_solving.word_equation_solving import (
    WordEquationSolving,
    _search_unique,
    _solves,
)


def _make(seed=0, n=12, level=None):
    import random

    task = WordEquationSolving()
    if level is not None:
        task.config.set_level(level)
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        rng.random()
        out.append(task.generate_example())
    return out


def _score(ex):
    return WordEquationSolving().score_answer(ex.answer, ex)


def test_generate_and_score_roundtrip():
    for ex in _make(n=15):
        assert _score(ex) == 1.0
        assert ex.metadata["mode"] in ("unique", "solutions", "unsat")


def test_all_levels_produce_every_mode():
    for level in range(7):
        seen = set()
        for ex in _make(seed=level, n=25, level=level):
            assert _score(ex) == 1.0
            seen.add(ex.metadata["mode"])
        assert seen == {"unique", "solutions", "unsat"}, level


def test_gold_answers_match_recomputed_solver_and_domain():
    for level in range(7):
        for ex in _make(seed=200 + level, n=12, level=level):
            abc = list(ex.metadata["alphabet"])
            cap = ex.metadata["max_binding"]
            sols = _search_unique(ex.metadata["lhs"], ex.metadata["rhs"],
                                  ex.metadata["vars"], abc, cap)
            if ex.metadata["mode"] == "unsat":
                assert len(sols) == 0
            elif ex.metadata["mode"] == "unique":
                assert len(sols) == 1
                b = dict(zip(ex.metadata["vars"], sols[0]))
                assert ex.answer == ",".join("%s=%s" % (v, b[v]) for v in sorted(ex.metadata["vars"]))
                assert _solves(ex.metadata["lhs"], ex.metadata["rhs"],
                               ex.metadata["vars"], b)
            else:
                assert ex.answer == str(len(sols))
                assert int(ex.answer) >= 1


def test_metadata_json_serializable():
    for ex in _make(n=10):
        json.dumps(ex.metadata)


def test_junk_and_wrong_answers_score_low():
    task = WordEquationSolving()
    examples = _make(n=40)
    assert task.score_answer("", examples[0]) == 0.0
    assert task.score_answer(None, examples[0]) == 0.0
    assert task.score_answer("garbage", examples[0]) == 0.0
    wrong = 0
    for ex in examples:
        mode = ex.metadata["mode"]
        if mode == "unique":
            bad = "x?=1,junk" if "x" not in ex.answer else "z?=1,!"
            assert task.score_answer(bad, ex) == 0.0
        elif mode == "solutions":
            assert task.score_answer(str(int(ex.answer) + 1), ex) == 0.0
        else:
            assert task.score_answer("satisfiable", ex) == 0.0
        wrong += 1
    assert wrong > 0


def test_level_changes_config():
    task = WordEquationSolving()
    t0 = (task.config.num_vars, task.config.max_len)
    task.config.set_level(6)
    assert task.config.num_vars >= t0[0]
    assert task.config.max_len >= t0[1]


def test_default_config_is_cheap_and_diverse():
    modes = {ex.metadata["mode"] for ex in _make(n=40)}
    assert modes == {"unique", "solutions", "unsat"}
