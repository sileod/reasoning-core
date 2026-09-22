import json
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround
from reasoning_core.tasks.generated.jev._common import canonical_json, choice_answer, jev_prompt, json_score, noul_answer, score_answer


INTENTS = {
    "billing": "Payments, invoices, refunds, or charges.",
    "access": "Authentication, permissions, or account access.",
    "technical": "Product failures, bugs, or integrations.",
    "other": "None of the other options clearly fits.",
}
IMPACT = [
    "Minor inconvenience; normal work can continue.",
    "Important workflow is degraded but a workaround exists.",
    "Core work is blocked and no workaround is available.",
]


@dataclass
class JevMultiViewAdjudicationConfig(Config):
    n_events: int = 4
    n_distractors: int = 2

    def apply_difficulty(self, level):
        self.n_events = sround(self.n_events + 1.2 * level)
        self.n_distractors = sround(self.n_distractors + 0.8 * level)


class JevMultiViewAdjudication(Task):
    summary = "Answer parallel Jev choice, noul, and score judgments over one joined operational state with relevant and distracting records."
    config_cls = JevMultiViewAdjudicationConfig

    def generate_entry(self):
        intent = random.choice(list(INTENTS))
        urgent = random.random() < 0.5
        impact = random.randrange(len(IMPACT))
        issue = {
            "billing": "The latest invoice contains a duplicate charge.",
            "access": "The user cannot sign in after the role change.",
            "technical": "The production integration returns errors on every request.",
            "other": "The user asks where to find the product roadmap.",
        }[intent]
        urgency = " This must be resolved today." if urgent else " There is no stated deadline."
        impact_text = [
            "The user can continue normal work.",
            "A documented workaround keeps the workflow usable.",
            "No workaround is available and the user's core workflow is blocked.",
        ][impact]
        events = [
            {"ts": i + 1, "kind": random.choice(["login", "note", "sync", "payment"]), "ok": random.choice([True, False])}
            for i in range(max(2, self.config.n_events))
        ]
        distractors = [
            {"id": f"D{i+1}", "kind": random.choice(["campaign", "survey", "feature_flag"]), "active": random.choice([True, False])}
            for i in range(max(0, self.config.n_distractors))
        ]
        state = {
            "ticket": {"message": issue + urgency + " " + impact_text, "channel": random.choice(["email", "chat", "api"])},
            "account": {"tier": random.choice(["free", "team", "enterprise"]), "status": "active"},
            "recent_events": events,
            "unrelated_records": distractors,
        }
        questions = {
            "intent": {"type": "choice", "instructions": "What is the primary operational issue in ticket.message?", "criteria": INTENTS},
            "is_urgent": {"type": "noul", "instructions": "Does ticket.message explicitly state time pressure or a deadline?"},
            "workflow_impact": {"type": "score", "instructions": "How much does the issue block the user's work?", "criteria": IMPACT},
        }
        answers = {
            "intent": choice_answer(intent, list(INTENTS)),
            "is_urgent": noul_answer(urgent),
            "workflow_impact": score_answer(impact, IMPACT),
        }
        return Entry(metadata=edict(state=state, questions=questions), answer=canonical_json(answers))

    def render_prompt(self, m):
        return jev_prompt(m.state, m.questions)

    def score_answer(self, answer, entry):
        return json_score(answer, entry)

    def balancing_key(self, problem):
        return json.loads(problem.answer)["intent"]["choice"]
