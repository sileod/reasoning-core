"""Compare two insurance policy texts and decide whether they pay identically.

Two policy descriptions share shuffled clause order and reworded synonyms; the
solver must decide whether they produce identical payouts on every possible loss
history, accounting for per-item and per-occurrence deductibles, per-item caps,
aggregate caps, exclusions, and limit reinstatement.
"""

import copy
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'loss_coverage_equivalence (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_cognitive_psychology_r4/loss_coverage_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_ITEM_POOL = [
    "plumbing fixtures",
    "electronic equipment",
    "kitchen appliances",
    "outdoor structures",
    "home office gear",
    "garden tools",
]

_OCC_TEMPLATES = [
    "A deductible of {occ} dollars is deducted from every single occurrence.",
    "Each loss occurrence is reduced by a {occ} dollar deductible.",
    "The insured bears a {occ} dollar deductible on every occurrence.",
    "Every occurrence is subject to a {occ} dollar deductible.",
]
_AGG_TEMPLATES = [
    "Combined annual payouts are capped at {agg} dollars.",
    "Total payout over the year may not exceed {agg} dollars.",
    "The policy pays no more than {agg} dollars across all claims annually.",
    "All claims together are limited to {agg} dollars per year.",
]
_REINST_TRUE = [
    "The annual limit is reinstated after each occurrence.",
    "The yearly limit refreshes and is reset after every claim.",
    "Each occurrence receives a fresh annual limit once the previous one is spent.",
]
_REINST_FALSE = [
    "The annual limit is a hard total and is not reinstated.",
    "The yearly cap is exhausted once reached and never refreshes.",
    "There is no reinstatement; the annual limit applies once across all claims.",
]
_ITEM_CLAUSE = [
    "Payouts for {item} are reduced by a {ded} dollar deductible and limited to {cap} dollars per year.",
    "{item} carries a per-item deductible of {ded} dollars and an annual cap of {cap} dollars.",
    "On {item} the insured pays the first {ded} dollars and claims top out at {cap} dollars.",
    "Claims on {item} are subject to a {ded} dollar deductible and a {cap} dollar yearly cap.",
]
_ITEM_EXCL = [
    "{item} is excluded from coverage entirely.",
    "No payment is ever made for losses to {item}.",
    "{item} is not covered at all under this policy.",
]


def _pick(templates):
    return templates[random.randrange(len(templates))]


@dataclass
class LossCoverageConfig(Config):
    num_items: int = 2
    max_amount: int = 400

    def apply_difficulty(self, level):
        self.num_items = 2 + (level + 1) // 2
        self.max_amount = 400 + level * 700


class LossCoverageEquivalence(Task):
    summary = ("Compare insurances with per-item and per-occurrence deductibles, per-item caps, "
               "aggregate caps, exclusions and limit reinstatement across shuffled, synonym "
               "reworded clause orders; answer 'same' or 'different' for identical payouts.")
    config_cls = LossCoverageConfig
    task_version = 2

    def _make_policy(self):
        names = random.sample(_ITEM_POOL, self.config.num_items)
        max_amt = self.config.max_amount
        items = []
        for nm in names:
            excluded = random.random() < 0.25
            cap = random.randint(max(120, max_amt // 2), max_amt)
            items.append({
                "name": nm,
                "ded": random.randint(5, 30),
                "cap": cap,
                "excluded": excluded,
            })
        return {
            "occ_ded": random.randint(5, 30),
            "agg_cap": random.randint(max_amt, max_amt * 2),
            "reinstated": random.choice([True, False]),
            "items": items,
        }

    def _render(self, policy):
        clauses = [_pick(_OCC_TEMPLATES).format(occ=policy["occ_ded"])]
        clauses.append(_pick(_AGG_TEMPLATES).format(agg=policy["agg_cap"]))
        clauses.append(_pick(_REINST_TRUE if policy["reinstated"] else _REINST_FALSE))
        for it in policy["items"]:
            if it["excluded"]:
                clauses.append(_pick(_ITEM_EXCL).format(item=it["name"]))
            else:
                clauses.append(_pick(_ITEM_CLAUSE).format(
                    item=it["name"], ded=it["ded"], cap=it["cap"]))
        random.shuffle(clauses)
        return "\n".join(clauses)

    def generate_entry(self):
        policy_a = self._make_policy()
        label = random.choice(["same", "different"])
        if label == "same":
            policy_b = copy.deepcopy(policy_a)
        else:
            policy_b = None
            for _ in range(40):
                cand = self._perturb(policy_a)
                if self._differs(policy_a, cand):
                    policy_b = cand
                    break
            if policy_b is None:
                raise RuntimeError("loss_coverage_equivalence: no verified perturbation found")
        same = not self._differs(policy_a, policy_b)
        if label == "same":
            assert same, "same-payout policy must not differ on probes"
        else:
            assert not same, "different-payout policy must differ on a probe"
        text_a = self._render(policy_a)
        text_b = self._render(policy_b)
        return Entry(
            metadata={
                "policy_a": text_a,
                "policy_b": text_b,
            },
            answer=label,
        )

    def _perturb(self, policy_a):
        p = copy.deepcopy(policy_a)
        kind = random.choice(["occ", "agg", "reinst", "item"])
        if kind == "occ":
            p["occ_ded"] += random.choice([3, 7, 11])
        elif kind == "agg":
            p["agg_cap"] *= 2
        elif kind == "reinst":
            p["reinstated"] = not p["reinstated"]
        else:
            i = random.randrange(len(p["items"]))
            sub = random.choice(["ded", "cap", "excl"])
            if sub == "ded":
                p["items"][i]["ded"] += random.choice([3, 7])
            elif sub == "cap":
                p["items"][i]["cap"] *= 2
            else:
                p["items"][i]["excluded"] = not p["items"][i]["excluded"]
        return p

    @staticmethod
    def _payout(policy, events):
        occ_ded = policy["occ_ded"]
        agg_cap = policy["agg_cap"]
        reinstated = policy["reinstated"]
        n = len(policy["items"])
        item_covered = [0] * n
        for (i, amt) in events:
            if policy["items"][i]["excluded"]:
                continue
            pre = amt - occ_ded
            if pre <= 0:
                continue
            if reinstated:
                pre = min(pre, agg_cap)
            item_covered[i] += pre
        finals = 0
        for i in range(n):
            f = item_covered[i] - policy["items"][i]["ded"]
            if f < 0:
                f = 0
            if f > policy["items"][i]["cap"]:
                f = policy["items"][i]["cap"]
            finals += f
        if not reinstated:
            finals = min(finals, agg_cap)
        return finals

    def _probes(self, policy):
        n = len(policy["items"])
        occ_ded = policy["occ_ded"]
        agg_cap = policy["agg_cap"]
        max_cap = max((it["cap"] for it in policy["items"]), default=1)
        max_amt = self.config.max_amount
        big = agg_cap + max_cap + max_amt + 2000
        probes = []
        for i in range(n):
            probes.append([(i, big)])
        for i in range(n):
            if not policy["items"][i]["excluded"]:
                probes.append([(i, big), (i, big)])
        for i in range(n):
            for j in range(i + 1, n):
                if not (policy["items"][i]["excluded"] and policy["items"][j]["excluded"]):
                    probes.append([(i, big), (j, big)])
        probes.append([(0, occ_ded)])
        probes.append([(0, occ_ded + 1)])
        probes.append([(0, occ_ded + occ_ded)])
        probes.append([(0, big), (0, big), (0, big)])
        return probes

    def _differs(self, a, b):
        pa = self._payout
        for probe in self._probes(a):
            if pa(a, probe) != pa(b, probe):
                return True
        return False

    def render_prompt(self, metadata):
        return (
            "Below are two insurance policy descriptions, Policy A and Policy B. "
            "Their clauses are written in a different order and possibly reworded.\n\n"
            "Policy A:\n" + metadata["policy_a"] + "\n\n"
            "Policy B:\n" + metadata["policy_b"] + "\n\n"
            "Do Policy A and Policy B produce identical payouts on every possible loss "
            "history, accounting for per-item and per-occurrence deductibles, per-item caps, "
            "aggregate caps, exclusions and limit reinstatement? Answer with exactly "
            "'same' or 'different'."
        )

    def score_answer(self, answer, entry):
        answer = str(answer).strip().lower()
        reference = str(entry["answer"]).strip().lower()
        return 1.0 if answer == reference else 0.0


design_choice = ("Present two insurance policy texts with shuffled clause order and reworded "
                 "synonyms; solvers answer 'same payout' or 'different' via semantic comparison.")
