import random
from dataclasses import dataclass, field
from typing import List

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'access_control_policy_evaluation (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:access_control_policy_evaluation',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/access_control_policy_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3953865554,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

PRECEDENCES = ["deny-overrides", "allow-overrides", "first-match"]


def _resolve(member_groups, action, precedence):
    if precedence == "deny-overrides":
        for g in member_groups:
            for rule in g["rules"]:
                if rule["action"] == action and rule["effect"] == "deny":
                    return "deny"
            for rule in g["rules"]:
                if rule["action"] == action and rule["effect"] == "allow":
                    return "allow"
        return "deny"
    if precedence == "allow-overrides":
        for g in member_groups:
            for rule in g["rules"]:
                if rule["action"] == action and rule["effect"] == "allow":
                    return "allow"
            for rule in g["rules"]:
                if rule["action"] == action and rule["effect"] == "deny":
                    return "deny"
        return "deny"
    if precedence == "first-match":
        for g in member_groups:
            for rule in g["rules"]:
                if rule["action"] == action:
                    return rule["effect"]
        return "deny"
    raise ValueError(precedence)


def _eval_counts(groups, action, precedence):
    counts = {"allow": 0, "deny": 0}
    for g in groups:
        for rule in g["rules"]:
            if rule["action"] == action:
                counts[rule["effect"]] += 1
    return counts


@dataclass
class AccessConfig(Config):
    num_groups: int = 3
    groups_per_subject: int = 2
    rules_per_group: int = 2
    num_actions: int = 3
    num_questions: int = 1

    def apply_difficulty(self, level):
        self.num_groups = self.num_groups + level
        self.groups_per_subject = min(2 + level, self.num_groups)
        self.rules_per_group = min(1 + level, 4)
        self.num_actions = min(3 + level, 5)
        self.num_questions = 1 + (level >= 3)


class AccessControlPolicyEvaluation(Task):
    summary = "Resolve inherited allow and deny permissions, group membership, and explicit exceptions under a stated precedence policy, returning effective access."
    config_cls = AccessConfig
    task_version = 2
    design_choice = "Instances present a subject with multiple group memberships, each carrying allow/deny rules; the solver must compute the effective decision after applying a stated precedence order (e.g., deny-overrides, allow-overrides, first-match)."

    def generate_entry(self):
        cfg = self.config
        actions = [f"act{i}" for i in range(cfg.num_actions)]

        while True:
            groups = []
            for gi in range(cfg.num_groups):
                rules = []
                for _ in range(cfg.rules_per_group):
                    action = random.choice(actions)
                    effect = random.choice(["allow", "deny"])
                    if not any(r["action"] == action for r in rules):
                        rules.append({"action": action, "effect": effect})
                groups.append({"name": f"group{gi}", "rules": rules})

            n = random.randint(2, cfg.num_groups)
            memberships = sorted(random.sample(list(range(cfg.num_groups)), n))
            member_groups = [groups[g] for g in memberships]
            precedence = random.choice(PRECEDENCES)

            questions = []
            for q in range(cfg.num_questions):
                action = random.choice(actions)
                outcome = _resolve(member_groups, action, precedence)
                questions.append({"action": action, "outcome": outcome})

            allow_deny = {q["outcome"] for q in questions}
            if len(allow_deny) < 2 and cfg.num_questions >= 2:
                continue

            if cfg.num_questions == 1:
                outcomes = [_resolve(member_groups, action, precedence) for action in actions]
                if len(set(outcomes)) < 2:
                    continue

            return Entry(
                metadata={
                    "subject": "subject",
                    "groups": member_groups,
                    "precedence": precedence,
                    "actions": actions,
                    "questions": questions,
                },
                answer=";".join(q["outcome"] for q in questions),
            )

    def render_prompt(self, metadata):
        lines = ["A subject belongs to the following groups, each with allow/deny rules."]
        lines.append(f"Precedence policy: {metadata['precedence']}.")
        for g in metadata["groups"]:
            rule_str = ", ".join(
                f"{r['action']}:{r['effect']}" for r in g["rules"]
            )
            lines.append(f"Group {g['name']}: {rule_str}.")
        if len(metadata["questions"]) > 1:
            lines.append(
                "For each question respond with allow or deny, listed in question order "
                "and separated by semicolons, e.g. 'allow;deny'."
            )
        else:
            lines.append("Respond with the exact word allow or deny.")
        for i, q in enumerate(metadata["questions"]):
            action = q["action"]
            lines.append(f"Question {i+1}: What is the effective decision for action {action}?")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        expected = [q["outcome"] for q in entry.metadata["questions"]]
        if not isinstance(answer, str):
            return 0.0
        given = [a.strip() for a in answer.split(";") if a.strip() != ""]
        if len(given) != len(expected):
            return 0.0
        if all(g == e for g, e in zip(given, expected)):
            return 1.0
        return 0.0


def resolve_answers(entry):
    return [q["outcome"] for q in entry.metadata["questions"]]
