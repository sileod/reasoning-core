"""The seam itself: what a question may be, what an answer is, and who decides.

The backend here answers from a dictionary, which is the whole point -- every test below
would pass against a chat model, a logit model, or a coin, because none of them is about
how an answer was produced. What they pin down is the split: policy reads answers, and a
backend never reads policy.
"""
import pytest

from reasoning_core.task_search import judge, validation
from reasoning_core.task_search.judge import Question, abstain, answer


class FakeJudge:
    """Answers from a script, and remembers what it was asked."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.asked = []

    def evaluate(self, state, questions):
        self.asked.append(state)
        reply = self.replies.pop(0) if self.replies else abstain("out of replies")
        return {question.name: reply for question in questions}


def test_a_question_is_a_choice_or_a_score_and_never_both_or_neither():
    Question("valid", "ask", choices=("VALID", "INVALID"))
    Question("novelty", "ask", score=(1, 5))
    with pytest.raises(ValueError):
        Question("confused", "ask", choices=("A", "B"), score=(1, 5))
    with pytest.raises(ValueError):
        Question("empty", "ask")
    with pytest.raises(ValueError):
        Question("lopsided", "ask", score=(1,))


def test_an_abstention_carries_a_reason_and_never_a_verdict():
    assert abstain("reviewer unreachable") == {
        "value": None, "probs": None, "reason": "reviewer unreachable"}
    assert answer(value="VALID")["probs"] is None


def test_a_purpose_picks_its_own_backend_before_the_global_one(monkeypatch):
    monkeypatch.delenv(judge.BACKEND_VAR, raising=False)
    monkeypatch.delenv("TASK_SEARCH_SANITY_BACKEND", raising=False)
    assert judge.backend_name("sanity") == judge.DEFAULT_BACKEND
    monkeypatch.setenv(judge.BACKEND_VAR, "jev")
    assert judge.backend_name("sanity") == "jev"
    monkeypatch.setenv("TASK_SEARCH_SANITY_BACKEND", "llm")
    assert judge.backend_name("sanity") == "llm"
    assert judge.backend_name("fidelity") == "jev"


def test_an_unknown_backend_is_named_in_the_error(monkeypatch):
    monkeypatch.setenv(judge.BACKEND_VAR, "oracle")
    with pytest.raises(ValueError, match="oracle"):
        judge.get_judge("fidelity")


def _votes(monkeypatch, *replies):
    fake = FakeJudge(*replies)
    monkeypatch.setattr(validation, "get_judge", lambda purpose: fake)
    verdict = validation._two_votes(
        "fidelity", "state", validation._FIDELITY, validation._FIDELITY_AGAIN,
        "SUBSTITUTES")
    return fake, verdict


def test_a_pass_needs_one_vote(monkeypatch):
    fake, verdict = _votes(monkeypatch, answer(value="REALIZES", reason="-"))
    assert verdict == {"verdict": "REALIZES", "why": "-"}
    assert len(fake.asked) == 1


def test_an_accusation_needs_a_second_reader_who_is_shown_the_first(monkeypatch):
    fake, verdict = _votes(
        monkeypatch,
        answer(value="SUBSTITUTES", reason="bare arithmetic"),
        answer(value="SUBSTITUTES", reason="agreed"))
    assert verdict == {"verdict": "SUBSTITUTES", "why": "agreed"}
    assert "FIRST REVIEWER: bare arithmetic" in fake.asked[1]


def test_an_unconfirmed_accusation_does_not_refuse_the_task(monkeypatch):
    _, verdict = _votes(
        monkeypatch,
        answer(value="SUBSTITUTES", reason="bare arithmetic"),
        answer(value="REALIZES", reason="the subject still does the work"))
    assert verdict["verdict"] == "REALIZES"
    assert "recheck did not confirm" in verdict["why"]
    assert "bare arithmetic" in verdict["why"]


def test_an_abstaining_backend_leaves_the_trial_unreviewed(monkeypatch):
    _, verdict = _votes(monkeypatch, abstain("reviewer unreachable: timed out"))
    assert verdict == {"verdict": None, "why": "reviewer unreachable: timed out"}
