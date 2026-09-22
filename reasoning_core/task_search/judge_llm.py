"""The judgment backend that asks a chat model, one question per call.

This is the transport the sanity and fidelity gates already used, moved behind the seam
without a byte of the request changing: same endpoint and model from the environment, same
temperature and budget, the question's instruction as the system message and the state as
the user message, and the same `VERDICT:` / `WHY:` pair read back out. That sameness is the
point -- it is what lets a second backend be measured against this one rather than against
a rewrite of it.

One question per call, because that is what the gates using it ask and inventing a
multi-question wire format with no caller would be guessing at requirements. The novelty
critic does batch, over candidates rather than questions, and it brings a JSON protocol of
its own that has survived several waves; when it moves behind this seam it arrives as a
second rendering here, written against what it actually needs.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

from .judge import abstain, answer

# The reviewer shares its provider quota with the workers it reviews, so a wave running
# eight at a time draws 429s that clear in seconds. One of those used to cost a trial its
# whole review -- the call fails open, so the gate passed the task unread rather than
# failing it. Wait the spike out instead.
RETRY_AFTER = (5, 20, 60)
TIMEOUT_SECONDS = 180
MAX_TOKENS = 512


def _post(request):
    for wait in RETRY_AFTER:
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.load(response)["choices"][0]["message"].get("content")
        except urllib.error.HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise
            time.sleep(wait)
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.load(response)["choices"][0]["message"].get("content")


class LLMJudge:
    """Answers typed questions by asking a chat model for a verdict and a reason."""

    def __init__(self, endpoint=None, model=None, key=None):
        key_name = os.environ.get("TASK_SEARCH_REVIEW_KEY_ENV", "")
        self.endpoint = endpoint or os.environ.get("TASK_SEARCH_REVIEW_ENDPOINT", "")
        self.model = model or os.environ.get("TASK_SEARCH_REVIEW_MODEL", "")
        self.key = key or (os.environ.get(key_name, "") if key_name else "")

    def evaluate(self, state, questions):
        """`{question name: normalized answer}`, abstaining wherever it cannot answer."""
        return {question.name: self._ask(state, question) for question in questions}

    def _ask(self, state, question):
        if not self.key or not self.endpoint or not self.model:
            return abstain("reviewer is not configured")
        body = json.dumps({
            "model": self.model,
            "temperature": 0,
            "max_tokens": MAX_TOKENS,
            "messages": [
                {"role": "system", "content": question.instruction},
                {"role": "user", "content": state},
            ],
        }).encode()
        request = urllib.request.Request(
            self.endpoint, body,
            {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        try:
            text = _post(request)
        except Exception as error:  # noqa: BLE001 - any transport fault is an abstention
            return abstain(f"reviewer unreachable: {error}")
        if not isinstance(text, str) or not text.strip():
            return abstain("reviewer returned no text")
        return _read(text, question)


def _read(text, question):
    """The verdict and the reason, or an abstention when the answer is unreadable.

    A model answering in a vocabulary nobody asked for is indistinguishable from one that
    did not answer, and has to be: every fidelity verdict recorded before the parser knew
    that gate's own words was `None`, silently, because it was still looking for `VALID`.
    So the question's outcomes are what the pattern is built from, and the reason survives
    either way -- an abstention that carries the model's own words back is what makes an
    unreviewed trial explainable afterwards.
    """
    reason = re.search(r"WHY:\s*(.+)", text)
    said = (reason.group(1).strip() if reason else text.strip())[:400]
    if question.score is not None:
        found = re.search(r"VERDICT:\s*(-?\d+)\b", text)
        low, high = question.score
        value = int(found.group(1)) if found else None
        if value is None or not low <= value <= high:
            return abstain(said)
        return answer(value=value, reason=said)
    found = re.search(r"VERDICT:\s*(" + "|".join(map(re.escape, question.choices)) + r")\b",
                      text)
    if not found:
        return abstain(said)
    return answer(value=found.group(1), reason=said)
