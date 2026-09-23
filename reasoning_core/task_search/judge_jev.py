"""The judgment backend that asks Jev, TypeSafe's typed-decision model, through OpenRouter.

Jev takes a state and named typed questions and returns a choice with a distribution over
the options, not text to parse, so this backend has no grammar to get wrong: the only
unreadable answer is a missing one. It is not a chat model -- OpenRouter refuses it on
`chat/completions` -- and every question in one `evaluate` goes out in a single request.

What it lacks is a reason. The gates record one with every verdict, so the reason here is
the distribution itself, which is what an operator reading a verdict later would want to
know about a model that does not explain itself.
"""
from __future__ import annotations

import json
import os
import urllib.request

from .judge import abstain, answer, post_json

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
DEFAULT_MODEL = "typesafe/jev-1.13"
KEY_VAR = "JEV_OPENROUTER_API_KEY"
# The gates' prose ends by telling a chat model how to format its reply. Jev replies in
# types, so that paragraph is an instruction about a wire format it does not use.
CHAT_FORMAT = "\n\nAnswer in this exact shape"


class JevJudge:
    """Answers choice questions with a distribution; abstains on anything else."""

    def __init__(self, key=None, model=None):
        self.key = key or os.environ.get(KEY_VAR, "")
        self.model = model or os.environ.get("TASK_SEARCH_JEV_MODEL", DEFAULT_MODEL)

    def evaluate(self, state, questions):
        if not self.key:
            return {question.name: abstain(f"{KEY_VAR} is not set") for question in questions}
        typed = [question for question in questions if question.choices]
        answers = {question.name: abstain("jev backend answers choice questions only")
                   for question in questions if not question.choices}
        if not typed:
            return answers
        body = json.dumps({
            "model": self.model,
            "state": state,
            "questions": {question.name: {
                "type": "choice",
                "instructions": question.instruction.split(CHAT_FORMAT, 1)[0],
                "criteria": {choice: choice for choice in question.choices},
            } for question in typed},
        }).encode()
        request = urllib.request.Request(
            ENDPOINT, body,
            {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        try:
            replies = post_json(request).get("answers") or {}
        except Exception as error:  # noqa: BLE001 - any transport fault is an abstention
            return {**answers, **{question.name: abstain(f"jev unreachable: {error}")
                                  for question in typed}}
        for question in typed:
            answers[question.name] = _read(replies.get(question.name), question)
        return answers


def _read(reply, question):
    """The choice and its distribution, or an abstention when Jev picked nothing asked for."""
    choice = (reply or {}).get("choice")
    if choice not in question.choices:
        return abstain(f"jev returned no usable choice: {json.dumps(reply)[:200]}")
    probs = {option: float((reply.get("probabilities") or {}).get(option, 0.0))
             for option in question.choices}
    return answer(value=choice, probs=probs,
                  reason="jev " + ", ".join(f"p({k})={v:.2f}" for k, v in probs.items()))
