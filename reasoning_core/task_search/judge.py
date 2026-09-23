"""Typed questions and answers: the one call a judgment backend has to implement.

A backend answers `evaluate(state, questions) -> {name: answer}` and never decides what an
answer means; two-vote rules, cutoffs and budgets stay with the gate that owns them. A
backend that cannot answer abstains -- `value` None, with a reason -- so a reviewer outage
leaves a trial unreviewed rather than rejected.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
import time
import urllib.error
import urllib.request


@dataclass(frozen=True)
class Question:
    """A choice between named outcomes. `instruction` is the gate's own prose, unchanged."""

    name: str
    instruction: str
    choices: tuple

    def __post_init__(self):
        if not self.choices:
            raise ValueError(f"question {self.name!r} needs choices")


def answer(value=None, probs=None, reason=None):
    """`probs` is None unless the backend has a real distribution to report."""
    return {"value": value, "probs": probs, "reason": reason}


def abstain(reason):
    return answer(reason=reason)


# Judges share provider quota with the workers they review, and a 429 used to cost a
# trial its whole review. Every HTTP backend waits the spike out the same way.
RETRY_AFTER = (5, 20, 60)
TIMEOUT_SECONDS = 180


def post_json(request):
    """The decoded JSON body, retrying rate limits and server errors; anything else raises."""
    for wait in RETRY_AFTER:
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise
            time.sleep(wait)
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.load(response)


DEFAULT_BACKEND = "llm"
BACKEND_VAR = "TASK_SEARCH_JUDGE_BACKEND"


def backend_name(purpose):
    """This purpose's own variable, then the global one, then llm -- so one gate can move."""
    return (os.environ.get(f"TASK_SEARCH_{purpose.upper()}_BACKEND")
            or os.environ.get(BACKEND_VAR)
            or DEFAULT_BACKEND)


def get_judge(purpose):
    name = backend_name(purpose)
    if name == "llm":
        from .judge_llm import LLMJudge

        return LLMJudge()
    if name == "jev":
        from .judge_jev import JevJudge

        return JevJudge()
    raise ValueError(
        f"unknown judge backend {name!r} for {purpose}: known backends are llm, jev")
