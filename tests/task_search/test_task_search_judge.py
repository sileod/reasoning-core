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


def test_a_question_needs_choices():
    Question("valid", "ask", choices=("VALID", "INVALID"))
    with pytest.raises(ValueError):
        Question("empty", "ask", choices=())


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


def _votes(monkeypatch, *replies, show_first=False):
    fake = FakeJudge(*replies)
    monkeypatch.setattr(validation, "get_judge", lambda purpose: fake)
    verdict = validation._two_votes(
        "fidelity", "state", validation._FIDELITY, validation._FIDELITY_AGAIN,
        "SUBSTITUTES", show_first=show_first)
    return fake, verdict


def test_a_pass_needs_one_vote(monkeypatch):
    fake, verdict = _votes(monkeypatch, answer(value="REALIZES", reason="-"))
    assert verdict == {"verdict": "REALIZES", "why": "-"}
    assert len(fake.asked) == 1


def test_an_accusation_needs_a_second_reader(monkeypatch):
    fake, verdict = _votes(
        monkeypatch,
        answer(value="SUBSTITUTES", reason="bare arithmetic"),
        answer(value="SUBSTITUTES", reason="agreed"))
    assert verdict == {"verdict": "SUBSTITUTES", "why": "agreed"}
    assert len(fake.asked) == 2


@pytest.mark.parametrize("show_first", [True, False])
def test_the_gate_decides_whether_the_second_reader_sees_the_first(monkeypatch, show_first):
    fake, _ = _votes(
        monkeypatch,
        answer(value="SUBSTITUTES", reason="bare arithmetic"),
        answer(value="SUBSTITUTES", reason="agreed"),
        show_first=show_first)
    assert ("FIRST REVIEWER: bare arithmetic" in fake.asked[1]) is show_first


def test_fidelity_rechecks_blind_and_sanity_shows_the_accusation(tmp_path, monkeypatch):
    """Fidelity's sentence only persuades; sanity's names the example that fails."""
    monkeypatch.setenv("TASK_SEARCH_REVIEW_KEY_ENV", "FAKE_REVIEW_KEY")
    monkeypatch.setenv("FAKE_REVIEW_KEY", "x")
    samples = tmp_path / "samples.md"
    samples.write_text("example")
    for gate, accusing in ((validation._sample_fidelity, "SUBSTITUTES"),
                           (validation._sample_sanity, "INVALID")):
        fake = FakeJudge(answer(value=accusing, reason="the accusation"),
                         answer(value=accusing, reason="agreed"))
        monkeypatch.setattr(validation, "get_judge", lambda purpose: fake)
        gate(samples)
        shown = "FIRST REVIEWER: the accusation" in fake.asked[1]
        assert shown is (gate is validation._sample_sanity)


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


def _jev_replying(monkeypatch, reply=None, error=None):
    """Fake the decisions endpoint; return the list of request bodies it received."""
    import io
    import json

    from reasoning_core.task_search import judge_jev

    sent = []

    def opener(request, timeout=None):
        sent.append(json.loads(request.data))
        if error:
            raise error
        return io.BytesIO(json.dumps(reply).encode())

    monkeypatch.setattr(judge_jev.urllib.request, "urlopen", opener)
    return judge_jev.JevJudge(key="k"), sent


def test_jev_asks_every_question_in_one_request_without_the_chat_format(monkeypatch):
    judge_, sent = _jev_replying(monkeypatch, {"answers": {
        "valid": {"type": "choice", "choice": "INVALID",
                  "probabilities": {"INVALID": 0.9, "VALID": 0.1}}}})
    got = judge_.evaluate("state", [validation._SANITY])["valid"]
    assert got["value"] == "INVALID"
    assert got["probs"] == {"VALID": 0.1, "INVALID": 0.9}
    assert len(sent) == 1
    asked = sent[0]["questions"]["valid"]
    assert set(asked["criteria"]) == {"VALID", "INVALID"}
    assert "VERDICT:" not in asked["instructions"]


@pytest.mark.parametrize("reply, error", [
    ({"answers": {"valid": {"choice": "MAYBE"}}}, None),
    ({"answers": {}}, None),
    (None, OSError("connection reset")),
])
def test_jev_abstains_rather_than_inventing_a_verdict(monkeypatch, reply, error):
    judge_, _ = _jev_replying(monkeypatch, reply, error)
    got = judge_.evaluate("state", [validation._SANITY])["valid"]
    assert got["value"] is None and got["reason"]


def test_jev_abstains_without_a_key(monkeypatch):
    from reasoning_core.task_search import judge_jev

    monkeypatch.delenv(judge_jev.KEY_VAR, raising=False)
    assert judge_jev.JevJudge().evaluate("s", [validation._SANITY])["valid"]["value"] is None


def test_the_jev_backend_is_selectable_per_purpose(monkeypatch):
    from reasoning_core.task_search.judge_jev import JevJudge

    monkeypatch.setenv("TASK_SEARCH_FIDELITY_BACKEND", "jev")
    assert isinstance(judge.get_judge("fidelity"), JevJudge)
