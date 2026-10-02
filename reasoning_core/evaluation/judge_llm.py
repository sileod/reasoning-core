"""The judgment backend that asks a chat model, one question per call.

The request is the one the gates always sent -- the question's prose as the system message,
the state as the user message -- and the `VERDICT:` / `WHY:` pair is read back out.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

from .judge import abstain, answer, post_json

MAX_TOKENS = 512
ENDPOINT_VAR = "RC_JUDGE_ENDPOINT"
MODEL_VAR = "RC_JUDGE_MODEL"
# Names the variable holding the key, so the key itself never sits in a config file.
KEY_ENV_VAR = "RC_JUDGE_KEY_ENV"


def configured_key():
    """(name of the key variable, its value); empty strings when either is unset."""
    name = os.environ.get(KEY_ENV_VAR, "")
    return name, os.environ.get(name, "") if name else ""


def _post(request):
    return post_json(request)["choices"][0]["message"].get("content")


class LLMJudge:
    """Answers typed questions by asking a chat model for a verdict and a reason."""

    def __init__(self, endpoint=None, model=None, key=None):
        self.endpoint = endpoint or os.environ.get(ENDPOINT_VAR, "")
        self.model = model or os.environ.get(MODEL_VAR, "")
        self.key = key or configured_key()[1]

    def evaluate(self, state, questions):
        """`{question name: normalized answer}`, abstaining wherever it cannot answer."""
        return {question.name: self._ask(state, question) for question in questions}

    def _ask(self, state, question):
        try:
            text = self.complete(question.instruction, state)
        except Exception as error:  # noqa: BLE001 - any transport fault is an abstention
            return abstain(f"reviewer unreachable: {error}")
        if not isinstance(text, str) or not text.strip():
            return abstain("reviewer returned no text")
        return _read(text, question)

    def complete(self, system, user, *, max_tokens=MAX_TOKENS, temperature=0):
        """The model's reply text; raises when unconfigured or unreachable."""
        if not self.key or not self.endpoint or not self.model:
            raise RuntimeError("reviewer is not configured")
        body = json.dumps({
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }).encode()
        request = urllib.request.Request(
            self.endpoint, body,
            {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        return _post(request)


def _read(text, question):
    """The verdict and reason, or an abstention that keeps the model's words.

    The pattern is built from the question's own choices: a parser hardcoded to one gate's
    vocabulary once read every fidelity verdict as None, silently, because the gate fails open.
    """
    reason = re.search(r"WHY:\s*(.+)", text)
    said = (reason.group(1).strip() if reason else text.strip())[:400]
    found = re.search(r"VERDICT:\s*(" + "|".join(map(re.escape, question.choices)) + r")\b",
                      text)
    if not found:
        return abstain(said)
    return answer(value=found.group(1), reason=said)
