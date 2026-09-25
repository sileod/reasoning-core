import random

from reasoning_core.tasks.generated.ua_state_tracking_r4.multiplicative_interaction_contrast.multiplicative_interaction_contrast import (
    MultiplicativeInteractionContrast,
    _parse_int,
)


def _task_at_level(level):
    t = MultiplicativeInteractionContrast()
    t.config.set_level(level)
    return t


def test_summary_literal():
    assert isinstance(MultiplicativeInteractionContrast.summary, str)
    assert "interaction contrast" in MultiplicativeInteractionContrast.summary


def test_design_choice_verbatim():
    assert MultiplicativeInteractionContrast.design_choice == (
        "Answer format: output the minimal positive integer scalar that restores "
        "invariance, with instances generated so the true scalar is always a prime "
        "between 2 and 97."
    )


def test_gold_answer_scores_one_all_levels():
    for level in range(7):
        t = _task_at_level(level)
        sample = t.generate_example()
        assert t.score_answer(sample.answer, sample) == 1.0


def test_answer_is_prime_between_2_and_97():
    t = _task_at_level(0)
    for _ in range(30):
        e = t.generate_entry()
        ans = int(e.answer)
        assert 2 <= ans <= 97
        assert ans in {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                       53, 59, 61, 67, 71, 73, 79, 83, 89, 97}


def test_contrast_is_consistent_in_metadata():
    t = _task_at_level(3)
    for _ in range(20):
        e = t.generate_entry()
        m = e.metadata
        assert m["contrast"] == m["true_scalar"]
        assert m["rescaled_target"] == m["table"][m["target"][0]][m["target"][1]]
        assert m["reference"] == m["table"][m["anchor"][0]][m["anchor"][1]]


def test_junk_scores_zero():
    t = MultiplicativeInteractionContrast()
    e = t.generate_entry()
    assert t.score_answer("", e) == 0.0
    assert t.score_answer("hello", e) == 0.0
    assert t.score_answer("-5", e) == 0.0
    assert t.score_answer("3.7", e) == 0.0


def test_wrong_prime_scores_zero():
    t = MultiplicativeInteractionContrast()
    for _ in range(20):
        e = t.generate_entry()
        wrong = str(((int(e.answer) % 20) + 5))
        if wrong == e.answer:
            wrong = str(int(e.answer) + 1)
            if wrong == e.answer:
                continue
        if int(wrong) <= 0:
            continue
        assert t.score_answer(wrong, e) == 0.0


def test_deterministic_under_seed():
    random.seed(123)
    a = MultiplicativeInteractionContrast()
    a.config.set_level(4)
    e1 = a.generate_entry()
    random.seed(123)
    b = MultiplicativeInteractionContrast()
    b.config.set_level(4)
    e2 = b.generate_entry()
    assert e1.answer == e2.answer
    assert e1.metadata["table"] == e2.metadata["table"]


def test_parse_int():
    assert _parse_int(" 13 ") == 13
    assert _parse_int("7") == 7
    assert _parse_int("x") is None
    assert _parse_int("0") is None
    assert _parse_int(None) is None
