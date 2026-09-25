"""Weighted-voting responsibility task.

Nominate one voter's actual vote and report its Chockler-Halpern degree of
responsibility for the positive outcome, or 'noncause'.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

NONCAUSE = "noncause"


@dataclass
class ResponsibilityConfig(Config):
    n: int = 3
    max_weight: int = 3

    def apply_difficulty(self, level):
        self.n = int(stochastic_rounding(3 + 2 * level))
        self.max_weight = min(10, 2 + level)


def minimal_contingency(weights, votes, nominated, threshold):
    """Min number of other yes-votes to flip so the nominated yes-vote is pivotal.

    Returns the integer k (count of flipped other voters), or None if the
    nominated vote cannot be made pivotal (noncause).
    """
    n = len(weights)
    w_x = weights[nominated]
    if not votes[nominated]:
        return None
    others_yes = [weights[i] for i in range(n) if i != nominated and votes[i]]
    s = sum(others_yes)
    lo = max(0, s - (threshold - 1))
    hi = s - (threshold - w_x)
    if hi < 0:
        return None
    cap = s
    inf = n + 1
    dp = [inf] * (cap + 1)
    dp[0] = 0
    for wt in others_yes:
        for tgt in range(cap, wt - 1, -1):
            cand = dp[tgt - wt] + 1
            if cand < dp[tgt]:
                dp[tgt] = cand
    best = inf
    for tgt in range(max(0, lo), hi + 1):
        if tgt <= cap and dp[tgt] < best:
            best = dp[tgt]
    if best >= inf:
        return None
    return best


class CausalContingencyResV3(Task):
    task_name = "causal_contingency_res"
    summary = (
        "Find the smallest admissible contingency making a nominated event "
        "necessary for an outcome in Boolean or threshold mechanisms with "
        "redundancy and preemption; return its responsibility score or noncause."
    )
    config_cls = ResponsibilityConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n
        maxw = cfg.max_weight
        for _ in range(60):
            weights = [random.randint(1, maxw) for _ in range(n)]
            nominated = random.randrange(n)
            noncause = random.random() < 0.45
            votes = [random.random() < 0.62 for _ in range(n)]
            votes[nominated] = not noncause
            total = sum(w for w, v in zip(weights, votes) if v)
            if total < 1:
                continue
            low = max(1, total - maxw - (n // 2))
            threshold = random.randint(low, total)
            if noncause:
                answer = NONCAUSE
                k = None
            else:
                k = minimal_contingency(weights, votes, nominated, threshold)
                if k is None:
                    continue
                answer = str(Fraction(1, k + 1))
            voters = [
                {"id": i, "weight": int(w), "vote": bool(v)}
                for i, (w, v) in enumerate(zip(weights, votes))
            ]
            meta = {
                "voters": voters,
                "threshold": int(threshold),
                "nominated": int(nominated),
                "nominated_vote": bool(votes[nominated]),
                "k": k if k is not None else None,
                "responsibility": answer,
            }
            return Entry(metadata=meta, answer=answer)
        raise RuntimeError("failed to generate a valid responsibility instance")

    def render_prompt(self, metadata):
        voters = metadata["voters"]
        wlist = ", ".join(
            f"V{v['id']}(w{v['weight']},{'yes' if v['vote'] else 'no'})"
            for v in voters
        )
        nidx = metadata["nominated"]
        vn = voters[nidx]
        return (
            "A weighted voting mechanism decides a binary outcome: outcome is 1 "
            "iff the total weight of the voters who vote yes is at least the "
            f"threshold T={metadata['threshold']}. The actual voters are "
            f"{wlist}, and the outcome is 1. "
            f"We nominate the event 'V{nidx} voted "
            f"{'yes' if vn['vote'] else 'no'}'.\n\n"
            "Under the Chockler-Halpern responsibility measure, the "
            "responsibility of this nominated actual vote for the outcome being "
            "1 is 1/(k+1), where k is the smallest number of other voters whose "
            "actual votes may be flipped so that the nominated vote becomes "
            "pivotal (flipping only the nominated vote, while others stay at "
            "their flipped contingency, would change the outcome to 0). If no "
            "such flip set exists - in particular whenever the nominated voter "
            "voted no - the nominated vote is a noncause (responsibility 0).\n\n"
            "What is the responsibility of the nominated vote? Answer with a "
            "fraction such as '1/2' or '1/3', or the word 'noncause'."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'causal_contingency_responsibility (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/causal_contingency_responsibility',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
