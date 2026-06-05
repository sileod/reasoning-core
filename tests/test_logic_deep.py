from reasoning_core import get_task, list_tasks, score_answer
from reasoning_core.tasks.logic_deep import Atom, PredSig, Rule, Theory, chase, close_with, render, support_sources


def test_multistep_nli_registers_and_generates():
    assert "multistep_nli" in list_tasks()
    assert "multistep_evidence_retrieval" in list_tasks()
    assert "multistep_abduction" in list_tasks()
    task = get_task("multistep_nli")
    seen = set()
    for _ in range(12):
        ex = task.generate_example(max_tokens=0)
        seen.add(ex.answer)
        assert ex.answer in {"entailment", "contradiction", "neutral"}
        assert score_answer(ex.answer, ex) == 1
        assert task.score_answer("not a label", ex) == 0
    assert len(seen) >= 2


def test_multistep_evidence_retrieval_generates():
    task = get_task("multistep_evidence_retrieval")
    ex = task.generate_example(max_tokens=0)
    assert ex.answer.startswith("[")
    assert ex.metadata.label in {"entailment", "contradiction"}
    assert ex.metadata.necessary_indices
    assert len(ex.metadata.valid_supports) == 1
    assert ex.metadata.support_indices == ex.metadata.valid_supports[0]
    assert ex.metadata.support_indices == ex.metadata.necessary_indices
    assert task.score_answer(ex.answer, ex) == 1
    assert task.score_answer("[]", ex) == float(ex.answer == "[]")


def test_multistep_abduction_generates():
    task = get_task("multistep_abduction")
    ex = task.generate_example(max_tokens=0)
    assert ex.answer.startswith("[")
    assert ex.metadata.label in {"entailment", "contradiction"}
    assert ex.metadata.candidates
    assert task.score_answer(ex.answer, ex) == 1


def test_chase_keeps_minimal_depth_derivation():
    sigs = {p: PredSig(p, ("person",)) for p in ("a", "b", "c")}
    theory = Theory(
        facts=[Atom("a", ("alice",))],
        rules=[
            Rule((Atom("a", ("?x",)),), Atom("b", ("?x",)), shape="u_imp"),
            Rule((Atom("b", ("?x",)),), Atom("c", ("?x",)), shape="u_imp"),
            Rule((Atom("a", ("?x",)),), Atom("c", ("?x",)), shape="u_imp"),
        ],
        denials=[],
        pred_sigs=sigs,
        entities={"person": ("alice",)},
    )
    res = chase(theory, max_depth=4)
    assert not res.inconsistent
    assert res.derivations[Atom("c", ("alice",))].depth == 1


def test_chase_saturates_when_depth_is_none():
    sigs = {p: PredSig(p, ("person",)) for p in ("a", "b", "c", "d")}
    rules = [
        Rule((Atom("a", ("?x",)),), Atom("b", ("?x",)), shape="u_imp"),
        Rule((Atom("b", ("?x",)),), Atom("c", ("?x",)), shape="u_imp"),
        Rule((Atom("c", ("?x",)),), Atom("d", ("?x",)), shape="u_imp"),
    ]
    theory = Theory([Atom("a", ("alice",))], rules, [], sigs, {"person": ("alice",)})
    assert Atom("d", ("alice",)) not in chase(theory, max_depth=2).closure
    assert Atom("d", ("alice",)) in chase(theory, max_depth=None).closure
    assert Atom("d", ("alice",)) in close_with(theory, []).closure


def test_support_sources_include_facts_and_rules():
    sigs = {p: PredSig(p, ("person",)) for p in ("a", "b")}
    rule = Rule((Atom("a", ("?x",)),), Atom("b", ("?x",)), shape="u_imp")
    theory = Theory([Atom("a", ("alice",))], [rule], [], sigs, {"person": ("alice",)})
    res = chase(theory, max_depth=None)
    _, source, _ = render(theory)
    assert support_sources(Atom("b", ("alice",)), res.derivations, source) == {0, 1}


def test_chase_self_loop_filter_is_pack_aware():
    sigs = {p: PredSig(p, ("entity", "entity")) for p in ("r",)}
    theory = Theory(
        facts=[Atom("r", ("a", "b")), Atom("r", ("b", "a"))],
        rules=[Rule((Atom("r", ("?x", "?y")), Atom("r", ("?y", "?z"))), Atom("r", ("?x", "?z")), shape="composition")],
        denials=[],
        pred_sigs=sigs,
        entities={"entity": ("a", "b")},
        domain_pack="surface",
    )
    res = chase(theory, max_depth=None)
    assert Atom("r", ("a", "a")) in res.closure

    theory.domain_pack = "spatial"
    res = chase(theory, max_depth=None)
    assert Atom("r", ("a", "a")) not in res.closure
    assert Atom("r", ("b", "b")) not in res.closure
