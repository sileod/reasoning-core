import random

from reasoning_core.tasks.generated.k3_operations_research_r4.prenex_skolem_clause_form.prenex_skolem_clause_form import (
    PrenexSkolemClauseForm,
    render_term,
)


def _make():
    t = PrenexSkolemClauseForm()
    t.config.set_level(0)
    return t


def test_generate_and_score():
    random.seed(1)
    t = _make()
    x = t.generate_example()
    assert t.score_answer(x.answer, x) == 1.0
    assert t.score_answer("", x) < 1.0
    assert t.score_answer("garbage", x) == 0.0


def test_both_modes_appear():
    random.seed(2)
    t = _make()
    modes = set()
    for _ in range(30):
        x = t.generate_example()
        modes.add(x.metadata["mode"])
    assert "skolem" in modes
    assert "clauses" in modes


def test_skolem_answer_is_term():
    random.seed(3)
    t = _make()
    seen = 0
    for _ in range(40):
        x = t.generate_example()
        if x.metadata["mode"] == "skolem":
            seen += 1
            ans = x.answer
            assert isinstance(ans, str) and ans
            assert "void" not in ans
    assert seen > 0


def test_clause_answer_not_empty():
    random.seed(4)
    t = _make()
    seen = 0
    for _ in range(40):
        x = t.generate_example()
        if x.metadata["mode"] == "clauses":
            seen += 1
            assert x.answer.startswith("{")
            assert "}" in x.answer
    assert seen > 0


def test_difficulty_changes():
    t = PrenexSkolemClauseForm()
    t.config.set_level(0)
    l0 = (t.config.n_quantifiers, t.config.atoms, t.config.arity)
    t.config.set_level(6)
    l6 = (t.config.n_quantifiers, t.config.atoms, t.config.arity)
    assert l6 != l0
    assert l6[0] > l0[0]


def test_every_level_generates():
    t = PrenexSkolemClauseForm()
    for lvl in (0, 1, 2, 3, 4, 5, 6):
        random.seed(10 + lvl)
        t.config.set_level(lvl)
        x = t.generate_example()
        assert t.score_answer(x.answer, x) == 1.0


def test_json_serializable_metadata():
    import json
    random.seed(5)
    t = _make()
    x = t.generate_example()
    json.dumps(x.metadata)


def test_render_term_str():
    assert render_term(('fun', 'sk1', ('x', 'y'))) == "sk1(x,y)"
    assert render_term("sk1") == "sk1"
