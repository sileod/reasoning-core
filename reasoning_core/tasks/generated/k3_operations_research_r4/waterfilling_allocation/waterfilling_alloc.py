import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'maxmin_waterfilling_allocation (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/maxmin_waterfilling_allocation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class WaterfillingConfig(Config):
    n_claims: int = 4
    claim_max: int = 30
    supply_lo: int = 1
    supply_hi: int = 20

    def apply_difficulty(self, level):
        self.n_claims = stochastic_rounding(4 + 2 * level)
        self.claim_max = stochastic_rounding(15 + 5 * level)
        self.supply_hi = stochastic_rounding(10 + 5 * level)


def waterfill_allocation(claims, supply):
    """Maximize the minimum satisfied allocation subject to sum(alloc)<=supply
    and 0<=alloc[i]<=claims[i]. Return the allocation.

    The optimal max-min allocation raises all unsatisfied claims together to a
    common level until one of them is saturated (reaches its cap) or the supply
    runs out, freezing saturated claims and re-levelling the remainder.
    """
    n = len(claims)
    alloc = [0] * n
    pending = sorted(range(n), key=lambda i: claims[i])
    remaining = float(supply)
    while pending and remaining > 0:
        used_pending = sum(alloc[i] for i in pending)
        n_pending = len(pending)
        min_cap = min(claims[i] for i in pending)
        max_raise = min(min_cap, (remaining + used_pending) / n_pending)
        for i in pending:
            alloc[i] = max(alloc[i], max_raise)
        used_now = sum(alloc[i] for i in pending)
        budget_used = used_now - used_pending
        remaining -= budget_used
        if budget_used <= 0:
            break
        frozen = [i for i in pending if alloc[i] >= claims[i]]
        pending = [i for i in pending if alloc[i] < claims[i]]
        if not frozen:
            break
    return alloc


class WaterfillingAllocation(Task):
    summary = ("Share a scarce divisible resource by raising unsatisfied claims toward one "
               "level until caps or supply bind: freeze saturated claims and re-level the "
               "remainder; answers are the allocation vector for integer claims under finite "
               "integer supply forcing partial freezing of some claims.")
    config_cls = WaterfillingConfig
    design_choice = ("Present claims as integer amounts and require the allocation vector as "
                     "a list of integers, with supply chosen to force partial freezing of "
                     "some claims.")

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_claims
        while True:
            claims = [random.randint(1, cfg.claim_max) for _ in range(n)]
            level = random.randint(1, cfg.claim_max)
            high = [c for c in claims if c > level]
            low = [c for c in claims if c < level]
            if not high or not low:
                continue
            alloc = [min(c, level) for c in claims]
            supply = sum(alloc)
            if supply <= 0:
                continue
            check = waterfill_allocation(claims, supply)
            if not all(abs(check[i] - alloc[i]) < 1e-9 for i in range(n)):
                continue
            break
        return Entry(
            metadata={
                "claims": claims,
                "supply": supply,
                "allocation": alloc,
            },
            answer=str(alloc),
        )

    def render_prompt(self, metadata):
        claims = metadata["claims"]
        supply = metadata["supply"]
        return (
            f"There are {len(claims)} claims for a divisible resource with a supply of "
            f"{supply} units. Claim {len(claims)} wants {claims[-1]} units at the most "
            f"and no claim may receive more than it asks. "
            f"For fairness you raise every unfulfilled claim toward one common level "
            f"until some claim reaches its cap or the supply runs out, then freeze the "
            f"saturated claims and re-level the rest, stopping when the whole supply is "
            f"used or every claim is capped. The claims are, in order: {claims}. "
            f"What allocation does every claim receive? Give the allocation as a list "
            f"of integers, one per claim in the same order, e.g. [1, 2, 3]."
        )

    def score_answer(self, answer, entry):
        import ast
        try:
            parsed = ast.literal_eval(answer.strip())
        except Exception:
            return 0.0
        if not isinstance(parsed, list) or len(parsed) != len(entry.metadata["claims"]):
            return 0.0
        gold = entry.metadata["allocation"]
        if all(isinstance(x, (int, float)) for x in parsed):
            try:
                return 1.0 if [int(x) for x in parsed] == gold else 0.0
            except Exception:
                return 0.0
        return 0.0

    def distractor_candidates(self, entry):
        claims = entry.metadata["claims"]
        supply = entry.metadata["supply"]
        cands = []
        total = sum(claims)
        if total >= supply:
            cands.append(str([supply, 0] + [0] * (len(claims) - 2)))
        cands.append(str([claims[-1]] + [0] * (len(claims) - 1)))
        cands.append(str([int(supply / len(claims))] * len(claims)))
        cands.append(str([c for c in claims]))
        return cands
