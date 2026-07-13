from reasoning_core.tasks.probabilistic_reasoning import evidence_grammar, mpe_answer


def test_mpe_answer_rejects_ties():
    tied = "0.5::a.\n0.5::b.\nobserved :- (a;b).\nevidence(observed,true)."
    unique = "0.7::a.\n0.2::b.\nobserved :- (a;b).\nevidence(observed,true)."

    assert mpe_answer(tied) is None
    assert mpe_answer(unique) == '["a", "not b"]'


def test_negated_conjunction_is_not_rendered_as_unless():
    rule = next(
        rule for rule in evidence_grammar()._instances
        if rule.templates.get("problog") == "({0},\\+{1})"
    )

    assert rule.templates["eng"].format("factor P", "A") == (
        "(factor P holds and factor A is false)"
    )
