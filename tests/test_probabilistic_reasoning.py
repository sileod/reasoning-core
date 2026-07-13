from collections import Counter

import pytest

from reasoning_core.tasks.probabilistic_reasoning import (
    MostProbableOutcome,
    evidence_grammar,
    mpe_answer,
)


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


def test_most_probable_outcome_is_stateless_and_batch_balanced():
    task = MostProbableOutcome()
    batch = task.generate_balanced_batch(batch_size=6)

    assert not hasattr(task, "_target_i")
    assert task.balancing_key_ratio == pytest.approx(1 / 3)
    assert Counter(problem.answer for problem in batch) == {"A": 2, "B": 2, "equal": 2}
