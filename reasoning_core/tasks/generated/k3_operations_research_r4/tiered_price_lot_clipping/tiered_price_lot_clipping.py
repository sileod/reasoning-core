import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'tiered_price_lot_clipping (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/tiered_price_lot_clipping',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                              'sandbox': {'name': 'bubblewrap',
                                          'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class TieredPriceConfig(Config):
    n_tiers_min: int = 2
    n_tiers_max: int = 3

    def apply_difficulty(self, level):
        self.n_tiers_min = 2
        self.n_tiers_max = 2 + int(level // 2)


def _gen_prices(n):
    while True:
        pool = random.sample(range(1, 41), n)
        ps = sorted(pool, reverse=True)
        if len(set(ps)) == n:
            return ps


def _gen_breaks(n):
    breaks = [0]
    cur = random.randint(6, 12)
    for _ in range(n - 1):
        cur += random.randint(3, 12)
        breaks.append(cur)
    return breaks


def _tier_total(q, p, D, h, A):
    return A * D / q + (h * p * q) / 2.0 + p * q


def _solve(breaks, prices, D, h, A):
    n = len(prices)
    candidates = []
    best = None
    bestq = None
    for i in range(n):
        p = prices[i]
        lo = breaks[i]
        hi = breaks[i + 1] if i + 1 < n else None
        denom = p * (h + 2)
        q_eoq = math.sqrt(2.0 * A * D / denom)
        cands = {lo}
        if hi is not None and hi > 1:
            cands.add(hi)
        for c in (math.floor(q_eoq), math.ceil(q_eoq)):
            cc = max(c, lo)
            if hi is not None:
                cc = min(cc, hi)
            cands.add(cc)
        for c in cands:
            if c < 1:
                continue
            if hi is not None and (c < lo or c > hi):
                continue
            if hi is None and c < lo:
                continue
            val = _tier_total(c, p, D, h, A)
            candidates.append(c)
            if best is None or val < best or (abs(val - best) < 1e-9 and c < bestq):
                best = val
                bestq = c
    if best is None:
        return None, None, []
    return best, bestq, candidates


class TieredPriceLotClipping(Task):
    summary = (
        "For stepped unit prices with 2-5 unequal-width tiers of strictly decreasing "
        "unit price, form each tier's unconstrained economic order quantity (EOQ), clip "
        "it into its price interval, then compare total ordering+holding+material cost "
        "at every surviving tier quantity and interval breakpoint; answers are the "
        "optimal integer lot size q, the minimal total annual cost, and the tie-free "
        "global optimum via exact cost comparison."
    )
    design_choice = (
        "Vary the number of price tiers from 2 to 5, with intervals of unequal widths "
        "and unit prices that are strictly decreasing but not necessarily proportional "
        "to interval size."
    )
    config_cls = TieredPriceConfig

    def generate_entry(self):
        while True:
            n = random.randint(self.config.n_tiers_min, self.config.n_tiers_max)
            breaks = _gen_breaks(n)
            prices = _gen_prices(n)
            D = random.randint(1000, 3000)
            h = random.randint(2, 8)
            A = random.randint(20, 120)
            best, qopt, candidates = _solve(breaks, prices, D, h, A)
            if best is None or qopt < 1:
                continue
            metadata = {
                "breaks": breaks,
                "prices": prices,
                "demand": D,
                "holding_mult": h,
                "order_cost": A,
                "qopt": int(qopt),
                "total_cost": float(best),
                "candidates": [int(c) for c in candidates],
            }
            return Entry(metadata=metadata, answer=f"{int(qopt)}|{best}")

    def render_prompt(self, metadata):
        breaks = metadata["breaks"]
        prices = metadata["prices"]
        D = metadata["demand"]
        h = metadata["holding_mult"]
        A = metadata["order_cost"]
        pieces = []
        for i in range(len(prices)):
            lo = breaks[i]
            hi = breaks[i + 1] if i + 1 < len(breaks) else "any amount at or above"
            pieces.append(f"quantities {lo}..{hi} cost ${prices[i]}/unit")
        tiers = "; ".join(pieces)
        return (
            f"A firm buys an item under a stepped unit price: {tiers}. All units in one "
            f"lot are charged that tier's unit price. Annual demand is {D} units, each "
            f"order costs ${A} to place, and holding cost is {h} times the unit price "
            f"paid, per unit per year. Minimizing total annual cost = ordering cost "
            f"({A}*{D}/q) + holding cost (({h}*unit price*q)/2) + material cost (q*unit "
            f"price), find the integer lot size q that achieves the minimum. Report "
            f"'q|cost' where q is that integer and cost is the minimal total annual "
            f"cost rounded to the nearest integer."
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry)


def _score(answer, entry):
    try:
        qs, cs = answer.split("|")
        q = int(qs.strip())
        c = float(cs.strip())
    except Exception:
        return 0.0
    gold_q = entry.metadata["qopt"]
    gold_c = entry.metadata["total_cost"]
    if q != gold_q:
        return 0.0
    if abs(c - gold_c) <= 0.5 + 1e-6:
        return 1.0
    return 0.0
