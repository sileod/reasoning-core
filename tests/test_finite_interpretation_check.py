import os

from reasoning_core.tasks._tptp_finite_interpretation import (
    FiniteInterpretation,
    complete_model,
    eval_cnf_clause,
    make_near_miss_model,
    parse_vampire_model,
    requirement_holds,
    requirements_hold,
    serialize_model,
    universally_quantify,
    write_signed_fmb_problem,
)


VAMPIRE_MODEL = """
% SZS output start FiniteModel for example
tff('declare_$i1',type,a:$i).
tff('declare_$i2',type,b:$i).
tff('finite_domain_$i',axiom,
      ! [X:$i] : (
         X = a | X = b
      ) ).

tff('distinct_domain_$i',axiom,
         a != b
).

tff(declare_f,type,f: ($i) > $i).
tff(function_f,axiom,
           f(a) = b
         & f(b) = a

).

tff(declare_p,type,p: ($i) > $o).
tff(predicate_p,axiom,
           p(a)
         & ~p(b)

).

% SZS output end FiniteModel for example
"""


def test_formula_evaluator_supports_emitted_cnf_subset():
    model = FiniteInterpretation(
        domain=[0, 1],
        constants={"a": 0, "b": 1},
        functions={"f": {(0,): 1, (1,): 0}},
        predicates={"p": {(0,): True, (1,): False}},
    )

    assert eval_cnf_clause("p(a) & ~p(b)", model)
    assert eval_cnf_clause("f(f(X)) = X", model)
    assert eval_cnf_clause("p(X) | ~p(X)", model)
    assert not eval_cnf_clause("p(X)", model)


def test_parse_and_totalize_vampire_model():
    partial = parse_vampire_model(VAMPIRE_MODEL)
    requirements = [
        {"formula": "p(a)", "should_be": True},
        {"formula": "~p(b)", "should_be": True},
        {"formula": "f(f(X)) = X", "should_be": True},
        {"formula": "p(X)", "should_be": False},
    ]
    model = complete_model(requirements, partial)

    assert model is not None
    assert requirements_hold(requirements, model)
    assert set(model.functions["f"]) == {(0,), (1,)}
    assert set(model.predicates["p"]) == {(0,), (1,)}


def test_near_miss_fails_only_one_or_two_requirements():
    requirements = [
        {"formula": "p(a)", "should_be": True},
        {"formula": "~p(b)", "should_be": True},
        {"formula": "a != b", "should_be": True},
    ]
    model = FiniteInterpretation(
        domain=[0, 1],
        constants={"a": 0, "b": 1},
        predicates={"p": {(0,): True, (1,): False}},
    )

    assert requirements_hold(requirements, model)
    negative = make_near_miss_model(requirements, model, max_tries=500)
    assert negative is not None
    assert not requirements_hold(requirements, negative)
    failures = sum(not requirement_holds(req, negative) for req in requirements)
    assert failures in (1, 2)


def test_signed_problem_writer_and_serialization():
    requirements = [
        {"formula": "p(X)", "should_be": True},
        {"formula": "q(X) | r(a)", "should_be": False},
    ]
    path = write_signed_fmb_problem(requirements)
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    finally:
        os.remove(path)

    assert "cnf(r_0, axiom, p(X))." in text
    assert "fof(r_1, axiom, ~(![X] : (q(X) | r(a))))." in text
    assert universally_quantify("p(a)") == "p(a)"

    model_text = serialize_model(FiniteInterpretation(domain=[0]))
    assert "Domain:\n{0}" in model_text
    assert "Constants:\n(none)" in model_text


def test_prompt_clarifies_false_universal_requirement():
    from reasoning_core.tasks.formal_maths import FiniteInterpretationCheck

    task = object.__new__(FiniteInterpretationCheck)
    prompt = task.prompt({
        "axiom_set": "GRP001-0.ax",
        "context_axioms": [],
        "requirements": [{"formula": "p(X)", "should_be": False}],
        "model": "Domain:\n{0}",
    })

    assert "at least one variable assignment" in prompt
    assert "The answer is `True`" in prompt
    assert "logic assistant" not in prompt
