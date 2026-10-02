"""The judgment backend that asks TypeSafe's Jev through OpenRouter's decisions endpoint.

Jev returns a typed choice with a distribution, not text, and gives no reason, so the
recorded reason is the distribution. All questions in one `evaluate` go in one request.
Measured against the LLM judge (2026-09-23): it tracks a blind LLM recheck on fidelity and
cannot tell right answers from wrong ones on sanity, which needs arithmetic it does not do.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.request

from .judge import abstain, answer, post_json

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
DEFAULT_MODEL = "typesafe/jev-1.13"
KEV_MODEL = "jaredpalmer/kev-4b"
KEY_VAR = "JEV_OPENROUTER_API_KEY"
# The key is shared with other OpenRouter use, so its dashboard total cannot say what Jev
# spent. Every call appends its reported cost here, and past the budget Jev abstains.
LEDGER = Path.home() / ".local" / "share" / "reasoning_core" / "jev_spend.tsv"
BUDGET_VAR = "JEV_BUDGET_USD"
DEFAULT_BUDGET_USD = 5.0
# The gates' prose ends by telling a chat model how to format its reply. Jev replies in
# types, so that paragraph is an instruction about a wire format it does not use.
CHAT_FORMAT = "\n\nAnswer in this exact shape"


class JevJudge:
    """Answers choice questions with a distribution."""

    def __init__(self, key=None, model=None, ledger=LEDGER):
        self.key = key or os.environ.get(KEY_VAR, "")
        self.model = model or os.environ.get("TASK_SEARCH_JEV_MODEL", DEFAULT_MODEL)
        self.ledger = ledger
        self.budget = float(os.environ.get(BUDGET_VAR, DEFAULT_BUDGET_USD))
        self.spent = (sum(float(line.split("\t")[1]) for line in ledger.read_text().splitlines())
                      if ledger.exists() else 0.0)

    def evaluate(self, state, questions):
        if not self.key:
            return {question.name: abstain(f"{KEY_VAR} is not set") for question in questions}
        if self.spent >= self.budget:
            return {question.name: abstain(f"jev has spent ${self.spent:.2f} of its "
                                           f"${self.budget:g} budget; raise {BUDGET_VAR}")
                    for question in questions}
        body = json.dumps({
            "model": self.model,
            "state": state,
            "questions": {question.name: {
                "type": "choice",
                "instructions": question.instruction.split(CHAT_FORMAT, 1)[0],
                "criteria": {choice: choice for choice in question.choices},
            } for question in questions},
        }).encode()
        request = urllib.request.Request(
            ENDPOINT, body,
            {"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
        try:
            reply = post_json(request)
        except Exception as error:  # noqa: BLE001 - any transport fault is an abstention
            return {question.name: abstain(f"jev unreachable: {error}") for question in questions}
        self._record(float((reply.get("usage") or {}).get("cost") or 0.0))
        replies = reply.get("answers") or {}
        return {question.name: _read(replies.get(question.name), question)
                for question in questions}

    def _record(self, cost):
        self.spent += cost
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a") as handle:
            handle.write(f"{self.model}\t{cost:.8f}\n")


def _read(reply, question):
    """The choice and its distribution, or an abstention when Jev picked nothing asked for."""
    choice = (reply or {}).get("choice")
    if choice not in question.choices:
        return abstain(f"jev returned no usable choice: {json.dumps(reply)[:200]}")
    probs = {option: float((reply.get("probabilities") or {}).get(option, 0.0))
             for option in question.choices}
    return answer(value=choice, probs=probs,
                  reason="jev " + ", ".join(f"p({k})={v:.2f}" for k, v in probs.items()))
