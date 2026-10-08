"""Apply prioritized policies to a request whose requester role is uncertain.

The role is known only through past request counts (the prior) and reports of stated reliability. Each decision
is the most probable outcome, and `soft` is its exact posterior pushed through the policy rules: P(allowed), the
distribution over the governing policy, and over the role. Problems where any top outcome leads by less than 0.1
are redrawn, and the allowed side is drawn first so a constant answer scores one half. Ported from
tasksource.jev.procedural.policy_under_uncertainty; its level tables stop at 4.
"""
import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.decision import Decision
from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

ROLES = ["analyst", "engineer", "manager"]
TEAMS = ["alpha", "beta", "gamma"]
ACTIONS = ["read", "write", "approve"]
SENSITIVITY = ["public", "internal", "restricted"]
RELIABILITY = [Fraction(2, 3), Fraction(3, 4), Fraction(4, 5), Fraction(9, 10)]
SOURCES = ["intake form", "directory lookup", "manager's note", "badge log"]
NONE = "none (default deny)"
N_POLICIES = [2, 3, 4, 6, 8]
N_REPORTS = [1, 1, 2, 3, 4]
PLURAL = {"analyst": "analysts", "engineer": "engineers", "manager": "managers"}
MARGIN = Fraction(1, 10)
SEMANTICS = (
    "A policy matches when all listed constraints match; max_sensitivity is the most sensitive resource allowed, in "
    "the order public < internal < restricted. Apply the matching policy with the highest priority, where a larger "
    "priority number wins; deny if none match. The requester's role is one of the roles in the history, in "
    "proportion to the history counts before the reports are considered. Each report is independent: it names the "
    "true role as often as its reliability says, and otherwise names one of the other possible roles, each equally "
    "likely.")


def _matches(policy, request):
    subject, rank = request["subject"], SENSITIVITY.index(request["resource"]["sensitivity"])
    return (subject["role"] in policy["roles"] and subject["team"] in policy["teams"]
            and subject["clearance"] >= policy["min_clearance"] and request["action"] in policy["actions"]
            and rank <= SENSITIVITY.index(policy["max_sensitivity"]))


def _governing(policies, request, role):
    request = {**request, "subject": {**request["subject"], "role": role}}
    return max((p for p in policies if _matches(p, request)), key=lambda p: p["priority"], default=None)


def _posterior(prior, reports, roles):
    """P(role | reports): a report names the true role with its reliability, else another possible role uniformly."""
    weights = {}
    for role in roles:
        weight = prior[role]
        for _, said, reliability in reports:
            weight *= reliability if said == role else (1 - reliability) / (len(roles) - 1)
        weights[role] = weight
    total = sum(weights.values())
    return {role: weight / total for role, weight in weights.items()}


def _decided(distribution):
    """The most probable outcome, if it leads the runner-up by at least MARGIN."""
    top, *rest = sorted(distribution.values(), reverse=True)
    return max(distribution, key=distribution.get) if top - max(rest, default=0) >= MARGIN else None


def _soft(distribution, options):
    """Floats for exact fractions over every option, summing to one."""
    values = {option: round(float(distribution.get(option, 0)), 6) for option in options}
    largest = max(values, key=values.get)
    values[largest] = round(values[largest] + 1.0 - sum(values.values()), 6)
    return values


def _policy(rng, i, n_policies):
    return {
        "id": f"P{i+1}",
        "priority": n_policies - i,
        "effect": rng.choice(["allow", "deny"]),
        "roles": sorted(rng.sample(ROLES, rng.randint(1, len(ROLES))), key=ROLES.index),
        "teams": sorted(rng.sample(TEAMS, rng.randint(1, len(TEAMS))), key=TEAMS.index),
        "min_clearance": rng.randrange(3),
        "actions": sorted(rng.sample(ACTIONS, rng.randint(1, len(ACTIONS))), key=ACTIONS.index),
        "max_sensitivity": rng.choice(SENSITIVITY),
    }


@dataclass
class PolicyUnderUncertaintyConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class PolicyUnderUncertainty(Task):
    summary = "Apply prioritized policies when the requester's role is only known through a prior and noisy reports."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or PolicyUnderUncertaintyConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        side = rng.random() < 0.5
        while True:
            problem = self._draw(rng, level)
            allowed, governing, posterior = problem[-3:]
            if (abs(allowed - Fraction(1, 2)) >= MARGIN and (allowed > Fraction(1, 2)) == side
                    and _decided(governing) and _decided(posterior)):
                break
        state, policies, roles = problem[:3]
        options = [p["id"] for p in policies] + [NONE]
        questions = {
            "access_allowed": Decision(side, type="noul", soft=round(float(allowed), 6), instructions=
                "Given the uncertainty about the requester's role, is the request more likely allowed than denied?"),
            "governing_policy": Decision(_decided(governing), criteria=dict.fromkeys(options),
                                         soft=_soft(governing, options),
                                         instructions="Which policy most likely governs the request?"),
            "requester_role": Decision(_decided(posterior), criteria=dict.fromkeys(roles), soft=_soft(posterior, roles),
                                       instructions="What is the requester's most likely role?"),
        }
        qid = question or random.choice(sorted(questions))
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])

    @staticmethod
    def _draw(rng, level):
        n_policies = max(2, sround(N_POLICIES[level] * rng.uniform(0.8, 1.2), seed=rng.random()))
        roles = sorted(rng.sample(ROLES, 2 if rng.random() < 0.6 - 0.1 * level else 3), key=ROLES.index)
        history = {role: rng.randint(2, 30) for role in roles}
        prior = {role: Fraction(count, sum(history.values())) for role, count in history.items()}
        true_role = rng.choices(roles, weights=[history[r] for r in roles])[0]
        reports = []
        for source in rng.sample(SOURCES, min(N_REPORTS[level], len(SOURCES))):
            reliability = rng.choice(RELIABILITY)
            said = true_role if rng.random() < reliability else rng.choice([r for r in roles if r != true_role])
            reports.append((source, said, reliability))

        subject = {"role": None, "team": rng.choice(TEAMS), "clearance": rng.randrange(3)}
        request = {"subject": subject, "resource": {"team": rng.choice(TEAMS), "sensitivity": rng.choice(SENSITIVITY)},
                   "action": rng.choice(ACTIONS)}
        role_matters = rng.random() < 0.7  # in the rest, the evidence about the role is irrelevant
        while True:
            policies = [_policy(rng, i, n_policies) for i in range(n_policies)]
            effects = {(_governing(policies, request, role) or {"effect": "deny"})["effect"] for role in roles}
            if (len(effects) > 1) == role_matters:
                break

        posterior = _posterior(prior, reports, roles)
        allowed, governing = Fraction(0), {}
        for role, p in posterior.items():
            policy = _governing(policies, request, role)
            key = policy["id"] if policy else NONE
            governing[key] = governing.get(key, 0) + p
            allowed += p if policy and policy["effect"] == "allow" else 0

        counts = ", ".join(f"{history[r]} by {PLURAL[r]}" for r in roles)
        state = {
            "request": {**request, "subject": {**subject, "role": "unknown"}},
            "role_evidence": {
                "history": f"Of the last {sum(history.values())} requests from this account, {counts}. "
                           "No other role has used it.",
                "reports": [{"source": source, "says": said,
                             "reliability": f"right {r.numerator} times in {r.denominator}"}
                            for source, said, r in reports],
            },
            "policies": policies,
            "semantics": SEMANTICS,
        }
        return state, policies, roles, allowed, governing, posterior
