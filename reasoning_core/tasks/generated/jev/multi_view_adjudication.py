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
BILLING_FLAGS = ["duplicate_charge", "invoice_mismatch", "refund_missing"]


@dataclass
class JevMultiViewAdjudicationConfig(Config):
    n_events: int = 4
    n_distractors: int = 2

    def apply_difficulty(self, level):
        self.n_events = sround(self.n_events + 1.2 * level)
        self.n_distractors = sround(self.n_distractors + 0.8 * level)


class JevMultiViewAdjudication(Task):
    summary = "Adjudicate intent, urgency, and workflow impact from cross-view operational signals under explicit precedence rules plus distracting records."
    task_version = 2
    config_cls = JevMultiViewAdjudicationConfig

    def generate_entry(self):
        intent = random.choice(list(INTENTS))
        urgent = random.random() < 0.5
        impact = random.randrange(len(IMPACT))

        billing = {flag: False for flag in BILLING_FLAGS}
        account = {
            "active": random.choice([True, False]),
            "auth_failures": random.choice([0, 1]),
            "permission_mismatch": False,
            "tier": random.choice(["free", "team", "enterprise"]),
        }
        telemetry = {
            "integration_failures": random.choice([0, 1]),
            "error_rate_percent": random.choice([0, 5, 10]),
        }

        if intent == "billing":
            billing[random.choice(BILLING_FLAGS)] = True
            if random.random() < 0.5:
                account.update(active=True, auth_failures=random.choice([2, 3]))
            if random.random() < 0.5:
                telemetry["integration_failures"] = random.choice([2, 3])
        elif intent == "access":
            account["active"] = True
            if random.random() < 0.5:
                account["auth_failures"] = random.choice([2, 3, 4])
            else:
                account["permission_mismatch"] = True
            if random.random() < 0.5:
                telemetry["error_rate_percent"] = random.choice([20, 35, 60])
        elif intent == "technical":
            account["permission_mismatch"] = False
            account["auth_failures"] = random.choice([0, 1])
            if random.random() < 0.5:
                telemetry["integration_failures"] = random.choice([2, 3, 4])
            else:
                telemetry["error_rate_percent"] = random.choice([20, 35, 60])

        if urgent:
            deadline_hours = random.choice([2, 8, 24, None])
            executive_escalation = deadline_hours is None or random.random() < 0.35
        else:
            deadline_hours = random.choice([None, 48, 72, 168])
            executive_escalation = False

        if impact == 0:
            workflow = {
                "core_blocked": False,
                "degraded": False,
                "workaround_available": random.choice([True, False]),
            }
        elif impact == 1:
            if random.random() < 0.5:
                workflow = {
                    "core_blocked": False,
                    "degraded": True,
                    "workaround_available": random.choice([True, False]),
                }
            else:
                workflow = {
                    "core_blocked": True,
                    "degraded": True,
                    "workaround_available": True,
                }
        else:
            workflow = {
                "core_blocked": True,
                "degraded": True,
                "workaround_available": False,
            }

        events = [
            {
                "ts": i + 1,
                "kind": random.choice(["login", "note", "sync", "payment"]),
                "ok": random.choice([True, False]),
            }
            for i in range(max(2, self.config.n_events))
        ]
        distractors = [
            {
                "id": f"D{i+1}",
                "kind": random.choice(["campaign", "survey", "feature_flag"]),
                "active": random.choice([True, False]),
            }
            for i in range(max(0, self.config.n_distractors))
        ]
        state = {
            "ticket": {
                "message": "The user reports an operational issue requiring adjudication from the joined records.",
                "channel": random.choice(["email", "chat", "api"]),
            },
            "billing": billing,
            "account": account,
            "telemetry": telemetry,
            "timeline": {
                "deadline_hours": deadline_hours,
                "executive_escalation": executive_escalation,
            },
            "workflow": workflow,
            "recent_events": events,
            "unrelated_records": distractors,
            "adjudication_rules": {
                "intent": (
                    "Choose billing if any billing flag is true. Otherwise choose access when account.active is true and "
                    "either account.auth_failures >= 2 or account.permission_mismatch is true. Otherwise choose technical "
                    "when telemetry.integration_failures >= 2 or telemetry.error_rate_percent >= 20. Otherwise choose other."
                ),
                "urgency": (
                    "Urgent iff timeline.executive_escalation is true or timeline.deadline_hours is not null and <= 24."
                ),
                "workflow_impact": (
                    "Use level 2 when workflow.core_blocked is true and no workaround is available; level 1 when "
                    "workflow.degraded is true or core work is blocked but a workaround is available; otherwise level 0."
                ),
                "scope": "recent_events and unrelated_records are distractors and do not override the joined current views.",
            },
        }
        questions = {
            "intent": {
                "type": "choice",
                "instructions": "Under state.adjudication_rules.intent, what is the primary operational issue?",
                "criteria": INTENTS,
            },
            "is_urgent": {
                "type": "noul",
                "instructions": "Under state.adjudication_rules.urgency, is this request urgent?",
            },
            "workflow_impact": {
                "type": "score",
                "instructions": "Under state.adjudication_rules.workflow_impact, how much does the issue block the user's work?",
                "criteria": IMPACT,
            },
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
