import json
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround
from reasoning_core.tasks.generated.jev._common import canonical_json, choice_answer, jev_prompt, json_score, noul_answer, score_answer


ROLES = ["analyst", "engineer", "manager"]
TEAMS = ["alpha", "beta", "gamma"]
ACTIONS = ["read", "write", "approve"]
SENSITIVITY = ["public", "internal", "restricted"]
RISK = ["Routine policy outcome.", "Sensitive or exceptional outcome requiring review.", "Denied high-risk request or policy conflict."]


def _matches(policy, request):
    return (
        request["subject"]["role"] in policy["roles"]
        and request["subject"]["team"] in policy["teams"]
        and request["subject"]["clearance"] >= policy["min_clearance"]
        and request["action"] in policy["actions"]
        and SENSITIVITY.index(request["resource"]["sensitivity"]) <= policy["max_sensitivity"]
    )


@dataclass
class JevPolicyApplicabilityConfig(Config):
    n_policies: int = 4

    def apply_difficulty(self, level):
        self.n_policies = sround(self.n_policies + 0.8 * level)


class JevPolicyApplicability(Task):
    summary = "Apply prioritized structured policies to an access request and return Jev authorization, governing-policy, and review-risk judgments."
    config_cls = JevPolicyApplicabilityConfig

    def generate_entry(self):
        request = {
            "subject": {"role": random.choice(ROLES), "team": random.choice(TEAMS), "clearance": random.randrange(3)},
            "resource": {"team": random.choice(TEAMS), "sensitivity": random.choice(SENSITIVITY)},
            "action": random.choice(ACTIONS),
        }
        policies = []
        n = max(2, self.config.n_policies)
        for i in range(n):
            policies.append({
                "id": f"P{i+1}",
                "priority": n - i,
                "effect": random.choice(["allow", "deny"]),
                "roles": random.sample(ROLES, random.randint(1, len(ROLES))),
                "teams": random.sample(TEAMS, random.randint(1, len(TEAMS))),
                "min_clearance": random.randrange(3),
                "actions": random.sample(ACTIONS, random.randint(1, len(ACTIONS))),
                "max_sensitivity": random.randrange(len(SENSITIVITY)),
            })
        policies[-1].update(
            roles=[request["subject"]["role"]],
            teams=[request["subject"]["team"]],
            min_clearance=request["subject"]["clearance"],
            actions=[request["action"]],
            max_sensitivity=SENSITIVITY.index(request["resource"]["sensitivity"]),
        )
        matching = [p for p in policies if _matches(p, request)]
        governing = max(matching, key=lambda p: p["priority"])
        allowed = governing["effect"] == "allow"
        conflict = len({p["effect"] for p in matching}) > 1
        risk_index = 2 if (not allowed and request["resource"]["sensitivity"] == "restricted") or conflict else 1 if request["resource"]["sensitivity"] == "restricted" else 0
        options = [p["id"] for p in policies]
        state = {
            "request": request,
            "policies": policies,
            "semantics": "A policy matches when all listed constraints match. Apply the highest-priority matching policy; default deny only if none match.",
        }
        questions = {
            "access_allowed": {"type": "noul", "instructions": "Does the governing policy allow the requested action?"},
            "governing_policy": {"type": "choice", "instructions": "Which matching policy has the highest priority?", "criteria": {x: x for x in options}},
            "review_risk": {"type": "score", "instructions": "How risky is this policy outcome for automated execution?", "criteria": RISK},
        }
        answers = {
            "access_allowed": noul_answer(allowed),
            "governing_policy": choice_answer(governing["id"], options),
            "review_risk": score_answer(risk_index, RISK),
        }
        return Entry(metadata=edict(state=state, questions=questions), answer=canonical_json(answers))

    def render_prompt(self, m):
        return jev_prompt(m.state, m.questions)

    def score_answer(self, answer, entry):
        return json_score(answer, entry)

    def balancing_key(self, problem):
        return int(json.loads(problem.answer)["access_allowed"]["noul"])
