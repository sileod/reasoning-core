import pytest

from reasoning_core.tasks.generated.wave12.access_control_policy_evaluation.access_control_policy_evaluation import (
    PRECEDENCES,
    AccessControlPolicyEvaluation,
    _resolve,
)

TASK = AccessControlPolicyEvaluation()


def test_generate_and_score():
    entry = TASK.generate_entry()
    assert TASK.score_answer(entry.answer, entry) == 1.0


def test_wrong_answer_scores_zero():
    entry = TASK.generate_entry()
    expected = [q["outcome"] for q in entry.metadata["questions"]]
    wrong = ["allow" if e == "deny" else "deny" for e in expected]
    assert TASK.score_answer(";".join(wrong), entry) == 0.0


def test_junk_scores_zero():
    entry = TASK.generate_entry()
    assert TASK.score_answer("", entry) == 0.0
    assert TASK.score_answer("not an answer", entry) == 0.0


def test_answer_format_is_yes_no():
    entry = TASK.generate_entry()
    expected = [q["outcome"] for q in entry.metadata["questions"]]
    for e in expected:
        assert e in ("allow", "deny")


def test_levels_generate():
    for level in range(7):
        cfg = AccessControlPolicyEvaluation().config_cls()
        cfg.set_level(level)
        TASK.config = cfg
        entry = TASK.generate_entry()
        assert TASK.score_answer(entry.answer, entry) == 1.0


def test_first_match_matches_rendered_order():
    cfg = AccessControlPolicyEvaluation().config_cls()
    cfg.set_level(0)
    orig = TASK.config
    TASK.config = cfg
    for _ in range(100):
        entry = TASK.generate_entry()
        md = entry.metadata
        if md["precedence"] != "first-match":
            continue
        for q in md["questions"]:
            got = _resolve(md["groups"], q["action"], "first-match")
            assert got == q["outcome"]
    TASK.config = orig


def test_validate():
    TASK.validate()
