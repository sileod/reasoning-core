import random

from reasoning_core.tasks.generated.k3_operations_research_r4.dpll_clause_search import (
    dpll_clause_search as mod,
)
from reasoning_core.tasks.generated.k3_operations_research_r4.dpll_clause_search.dpll_clause_search import (
    DpllClauseSearch,
    _make_cnf,
    _run,
    _parse_assignment,
    _parse_decision,
    _parse_conflict,
)


def test_generate_and_score_roundtrip():
    for level in (0, 2, 4, 6):
        mod._VERDICT_SEEN.clear()
        task = DpllClauseSearch(config=mod.DPLLClauseSearchConfig().set_level(level))
        task.config.set_level(level)
        seen = set()
        for _ in range(120):
            ex = task.generate_example()
            assert ex.metadata["mode"] in (
                "verdict", "assignment", "decision", "conflict")
            assert task.score_answer(ex.answer, ex) == 1.0
            if ex.metadata["mode"] == "verdict":
                seen.add(ex.answer)
        assert seen == {"SAT", "UNSAT"}, seen


def test_parsers():
    assert _parse_assignment("x1=T,x2=F") == {1: True, 2: False}
    assert _parse_assignment("x1=T, x2 = F") == {1: True, 2: False}
    assert _parse_assignment("nonsense") is None
    assert _parse_decision("x2,~x1,x3") == [(2, False), (1, True), (3, False)]
    assert _parse_decision("") is None
    assert _parse_conflict("~x1,x3") == {(1, True), (3, False)}


def test_make_cnf_covers_vars():
    random.seed(0)
    cfg = mod.DPLLClauseSearchConfig().set_level(2)
    for _ in range(200):
        c = _make_cnf(cfg)
        vars_used = {abs(l) for cl in c for l in cl}
        assert vars_used == set(range(1, cfg.num_vars + 1))


def test_dpll_answers_consistent():
    random.seed(1)
    sat = 0
    unsat = 0
    for _ in range(300):
        c = _make_cnf(mod.DPLLClauseSearchConfig().set_level(3))
        s, assign, decisions, first = _run(c)
        if s:
            sat += 1
            assert all(
                any(abs(l) in assign and assign[abs(l)] == (l > 0) for l in cl)
                for cl in c
            )
        else:
            unsat += 1
            assert first is not None
    assert sat > 0 and unsat > 0


def test_junk_scores_zero():
    task = DpllClauseSearch()
    ex = task.generate_example()
    for junk in ("", "import fakemodule", "xyz", "42"):
        assert task.score_answer(junk, ex) == 0.0


def _strip(ex):
    d = ex["metadata"]
    return {"prompt": ex["prompt"], "answer": ex["answer"],
            "metadata": {k: v for k, v in d.items() if k != "_time"}}


def test_deterministic_under_seed():
    mod._VERDICT_SEEN.clear()
    random.seed(4238614268)
    a = [_strip(el.to_dict()) for el in (DpllClauseSearch().generate_example() for _ in range(6))]
    mod._VERDICT_SEEN.clear()
    random.seed(4238614268)
    b = [_strip(el.to_dict()) for el in (DpllClauseSearch().generate_example() for _ in range(6))]
    assert a == b
