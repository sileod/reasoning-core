"""Typed questions, typed answers, and the one seam a judgment backend plugs into.

Three gates in this package ask a model to judge something: whether a candidate's gold
answers are right, whether it built the task that was assigned, and whether a proposal is
new. Each grew its own transport, its own prompt format and its own parser, so a fourth
gate meant a fourth copy and a second kind of judge meant editing all three.

The seam is one call. A backend answers questions; it never decides what an answer means.
Score floors, majority rules, two-vote confirmations, retirement budgets -- all of that is
policy, it lives with the gate that owns it, and a backend that knew about any of it would
have to be rewritten the next time a gate changed its mind. The test of the split is that
adding a backend touches no gate, and adding a gate touches no backend.

The contract that matters most here is abstention. Every credential path in this pipeline
fails open on purpose: a reviewer outage must not reject a task that is fine, so a backend
that cannot answer -- no key, no endpoint, unreachable, unparseable, answering in a
vocabulary nobody asked for -- returns `value: None` and says why. It never returns a
verdict it did not get. Gates read a `None` as "unreviewed", which is what they already
did, and the silence is the same silence they were written against.
"""
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Question:
    """One thing to decide, named so its answer can be found again.

    `instruction` is the whole of what the judge is told: the question, what counts as
    each answer, and what not to flag. It is prose because the gates that own these
    questions were written as prose and their wording is load-bearing -- `_FIDELITY_ASK`
    spends four paragraphs on what substitution is not, and each of them was added after a
    reviewer refused a task that was fine.

    A question is either a choice between named outcomes or a score in a range, never
    both and never neither.
    """

    name: str
    instruction: str
    choices: tuple = ()
    score: tuple = None

    def __post_init__(self):
        if bool(self.choices) == (self.score is not None):
            raise ValueError(
                f"question {self.name!r} must have choices or a score range, not both")
        if self.score is not None and len(self.score) != 2:
            raise ValueError(f"question {self.name!r} needs a (low, high) score range")


def answer(value=None, probs=None, reason=None):
    """One normalized answer. Every backend returns these and nothing else.

    `probs` is the distribution over the question's outcomes when the backend has one and
    `None` when it does not, which is the honest shape: a model that emits text has no
    distribution to report, and inventing a point mass at its own answer would make an
    unhedged guess indistinguishable from a confident one to anybody reading it later.
    """
    return {"value": value, "probs": probs, "reason": reason}


def abstain(reason):
    """The answer a backend gives when it has none. Never a verdict, always a reason."""
    return answer(reason=reason)


DEFAULT_BACKEND = "llm"
BACKEND_VAR = "TASK_SEARCH_JUDGE_BACKEND"


def backend_name(purpose):
    """Which backend answers this purpose: its own variable, then the global, then llm.

    Per-purpose before global so a gate can be moved to a new backend one at a time and
    measured against the ones that did not move, which is the only way to tell a cheaper
    judge from a worse one.
    """
    return (os.environ.get(f"TASK_SEARCH_{purpose.upper()}_BACKEND")
            or os.environ.get(BACKEND_VAR)
            or DEFAULT_BACKEND)


def get_judge(purpose):
    """The judge for one purpose, built fresh so a changed environment is read again."""
    name = backend_name(purpose)
    if name == "llm":
        from .judge_llm import LLMJudge

        return LLMJudge()
    raise ValueError(f"unknown judge backend {name!r} for {purpose}: known backends are llm")
