from reasoning_core.tasks.probabilistic_reasoning import mpe_answer


def test_mpe_answer_rejects_ties():
    tied = "0.5::a.\n0.5::b.\nobserved :- (a;b).\nevidence(observed,true)."
    unique = "0.7::a.\n0.2::b.\nobserved :- (a;b).\nevidence(observed,true)."

    assert mpe_answer(tied) is None
    assert mpe_answer(unique) == '["a", "not b"]'
