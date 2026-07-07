from reasoning_core import get_task, list_tasks, score_answer
from reasoning_core.tasks.logic_depth import (
    Atom,
    Denial,
    PredSig,
    Rule,
    Theory,
    _binary_query,
    chase,
    close_with,
    render,
    rule_text,
    support_sources,
)


def test_multistep_nli_registers_and_generates():
    assert "multistep_nli" in list_tasks()
    assert "multistep_evidence_retrieval" in list_tasks()
    assert "multistep_abduction" in list_tasks()
    assert "logic_qa" in list_tasks()
    task = get_task("multistep_nli")
    seen = set()
    for _ in range(12):
        ex = task.generate_example(max_tokens=0)
        seen.add(ex.answer)
        assert ex.answer in {"Yes", "No", "Maybe"}
        assert ex.metadata.label in {"entailment", "contradiction", "neutral"}
        assert score_answer(ex.answer, ex) == 1
        assert task.score_answer(ex.answer + ".", ex) == 1
        assert task.score_answer("not a label", ex) == 0
    assert len(seen) >= 2


def test_multistep_evidence_retrieval_generates():
    task = get_task("multistep_evidence_retrieval")
    ex = task.generate_example(max_tokens=0)
    assert ex.answer
    assert all(x.isdigit() for x in ex.answer.split())
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
    assert ex.answer
    assert all(x.isdigit() for x in ex.answer.split())
    assert ex.metadata.label in {"entailment", "contradiction"}
    assert ex.metadata.candidates
    assert task.score_answer(ex.answer, ex) == 1


def test_logic_qa_generates():
    task = get_task("logic_qa")
    seen = set()
    for _ in range(8):
        ex = task.generate_example(max_tokens=0)
        seen.add(ex.metadata.answer_mode)
        assert ex.metadata.answer_mode in {"count", "list"}
        assert ex.metadata.question
        if ex.answer not in {"0", "none"}:
            assert ex.metadata.support_indices
        assert task.score_answer(ex.answer, ex) == 1
    assert seen


def test_binary_logic_qa_questions_are_proof_oriented_and_grammatical():
    assert _binary_query("aunt_or_uncle", "alice", False, "kinship") == (
        "Which other entities can alice be shown to be an aunt or uncle of?"
    )
    assert _binary_query("contains", "box", True, "spatial") == (
        "How many other entities can box be shown to contain?"
    )
    assert _binary_query("helps", "clara", False, "surface") == (
        "Which other entities can clara be shown to stand in the helps relation to?"
    )


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


def test_negative_composition_head_uses_generic_signed_rule_text():
    rule = Rule(
        (Atom("helps", ("?x", "?y")), Atom("trusts", ("?y", "?z"))),
        Atom("advises", ("?x", "?z"), False),
        shape="composition",
    )
    text, _ = rule_text(rule, rid=0)
    assert "x does not stand in the advises relation to z" in text
    assert "the first advises the third" not in text


def test_negative_converse_head_uses_generic_signed_rule_text():
    rule = Rule(
        (Atom("helps", ("?x", "?y")),),
        Atom("trusts", ("?y", "?x"), False),
        shape="converse",
    )
    text, _ = rule_text(rule, rid=0)
    assert "y does not stand in the trusts relation to x" in text
    assert "the second trusts the first" not in text


def test_spatial_left_of_cycle_is_inconsistent_via_derived_self_loop():
    sigs = {"left_of": PredSig("left_of", ("item", "item"))}
    theory = Theory(
        facts=[Atom("left_of", ("a", "b")), Atom("left_of", ("b", "a"))],
        rules=[
            Rule(
                (Atom("left_of", ("?x", "?y")), Atom("left_of", ("?y", "?z"))),
                Atom("left_of", ("?x", "?z")),
                shape="composition",
            )
        ],
        denials=[Denial((Atom("left_of", ("?x", "?x")),))],
        pred_sigs=sigs,
        entities={"item": ("a", "b")},
        domain_pack="spatial",
    )
    res = chase(theory, max_depth=None)
    assert res.inconsistent
    assert Atom("left_of", ("a", "a")) in res.closure

def test_spatial_acyclic_left_of_chain_remains_consistent():
    sigs = {"left_of": PredSig("left_of", ("item", "item"))}
    theory = Theory(
        facts=[Atom("left_of", ("a", "b")), Atom("left_of", ("b", "c"))],
        rules=[
            Rule(
                (Atom("left_of", ("?x", "?y")), Atom("left_of", ("?y", "?z"))),
                Atom("left_of", ("?x", "?z")),
                shape="composition",
            )
        ],
        denials=[Denial((Atom("left_of", ("?x", "?x")),))],
        pred_sigs=sigs,
        entities={"item": ("a", "b", "c")},
        domain_pack="spatial",
    )
    res = chase(theory, max_depth=None)
    assert not res.inconsistent
    assert Atom("left_of", ("a", "c")) in res.closure
