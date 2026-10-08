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
# The decider asked by default for signals and answer audits. pplx won judge_bench v1 (2026-10-08) on
# every axis vs jev-1.13: wrong-answer AUROC .924 vs .880, 4-way pick .81 vs .74. Signal columns are
# keyed by this name, so old jev columns are never mixed with pplx answers.
DEFAULT_DECIDER = "pplx"
BACKEND_VAR = "RC_JUDGE_BACKEND"


def backend_name(purpose):
    """This purpose's own variable, then the global one, then llm -- so one gate can move."""
    return (os.environ.get(f"{BACKEND_VAR}_{purpose.upper()}")
            or os.environ.get(BACKEND_VAR)
            or DEFAULT_BACKEND)


def get_judge(purpose):
    return make_judge(backend_name(purpose), purpose)


def make_judge(name, purpose="signals"):
    if name == "llm":
        from .judge_llm import LLMJudge

        return LLMJudge()
    from .judge_jev import DECIDERS, JevJudge

    if name in DECIDERS:  # every decider answers the same decisions API; only the model differs
        return JevJudge(model=None if name == "jev" else DECIDERS[name])
    raise ValueError(f"unknown judge backend {name!r} for {purpose}: known backends are llm, "
                     + ", ".join(DECIDERS))
