"""The judgment backend that asks Respan's Span-01 whether a behaviour is present.

Span scores named behaviours as present, absent or not observable, so it answers two-way
questions only: the first choice is "present" and the second "absent", renormalised over
those two. A wider question abstains. The free tier has an unpublished daily cap, and a
refused or failed request is an abstention like any outage, after which this judge stops
asking for the rest of the process: a caller that also holds Jev keeps going without it.
Measured 2026-09-26: 0.34 s median, a little behind Jev on difficulty and well behind it
on telling a right reference answer from a wrong one (AUROC 0.63 against 0.87).
"""
from __future__ import annotations

import json
import os
import urllib.request

from .judge import abstain, answer, post_json

ENDPOINT = "https://api.respan.ai/api/v1/scores"
DEFAULT_MODEL = "span-01-free"
KEY_VAR = "RESPAN_API_KEY"


class SpanJudge:
    """Answers two-way questions with a distribution."""

    def __init__(self, key=None, model=None):
        self.key = key or os.environ.get(KEY_VAR, "")
        self.model = model or os.environ.get("TASK_SEARCH_SPAN_MODEL", DEFAULT_MODEL)
        self.down = None if self.key else f"{KEY_VAR} is not set"

    @staticmethod
    def answers(question):
        return len(question.choices) == 2

    def evaluate(self, state, questions):
        binary = [question for question in questions if self.answers(question)]
        results = self._score(state, binary) if binary and not self.down else {}
        return {question.name: _read(results.get(question.name), question, self.down)
                for question in questions}

    def _score(self, state, questions):
        body = json.dumps({
            "model": self.model,
            # Span reads a conversation; the whole state is the user's turn.
            "span": {"input": [{"role": "user", "content": state}],
                     "output": {"role": "assistant", "content": ""}},
            "behaviors": [{"id": question.name, "definition": question.instruction}
                          for question in questions],
        }).encode()
        request = urllib.request.Request(
            ENDPOINT, body,
            {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        try:
            return {row["id"]: row for row in post_json(request).get("results") or []}
        except Exception as error:  # noqa: BLE001 - any fault retires this judge
            self.down = f"span unreachable: {error}"
            return {}


def _read(row, question, down):
    if not SpanJudge.answers(question):
        return abstain("span answers two-way questions only")
    present, absent = (float((row or {}).get(key) or 0.0) for key in ("p_present", "p_absent"))
    if present + absent <= 0:
        return abstain(down or f"span returned nothing usable: {json.dumps(row)[:200]}")
    yes, no = question.choices
    probs = {yes: present / (present + absent), no: absent / (present + absent)}
    return answer(value=max(probs, key=probs.get), probs=probs,
                  reason="span " + ", ".join(f"p({k})={v:.2f}" for k, v in probs.items()))
