import heapq
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'recursive_equivalence_extraction (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/recursive_equivalence_extraction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

ORDER = ('add', 'sub', 'mul')
_MAX_EXPAND = 60000
_MAX_ATTEMPTS = 60


def make_opdefs(costs, budgets, maxv):
    ca, cs, cm = costs
    ba, bs, bm = budgets
    return {
        'add': (ca, ba, lambda a, b: a + b if a + b <= maxv else None),
        'sub': (cs, bs, lambda a, b: a - b if a >= b else None),
        'mul': (cm, bm, lambda a, b: a * b if a * b <= maxv else None),
    }


def min_cost(leaves, target, opdefs, maxv, inst_cap):
    start_set = frozenset(int(x) for x in leaves)
    if target in start_set:
        return 0
    nops = len(ORDER)
    start_bud = tuple(opdefs[nm][1] for nm in ORDER)
    start = (start_set, start_bud)
    dist = {start: 0}
    pq = [(0, start)]
    best = None
    expanded = 0
    while pq:
        d, st = heapq.heappop(pq)
        if d != dist.get(st):
            continue
        if best is not None and d >= best:
            continue
        expanded += 1
        if expanded > _MAX_EXPAND:
            return None
        sset, buds = st
        if target in sset:
            if best is None or d < best:
                best = d
            continue
        if len(sset) - len(start_set) >= inst_cap:
            continue
        vals = sorted(sset)
        for idx in range(nops):
            nm = ORDER[idx]
            cost, budget, fn = opdefs[nm]
            if buds[idx] == 0:
                continue
            for a in vals:
                for b in vals:
                    v = fn(a, b)
                    if v is None or v < 0 or v > maxv:
                        continue
                    if v in sset:
                        continue
                    ns = frozenset(sset) | {v}
                    nb = list(buds)
                    nb[idx] -= 1
                    nb = tuple(nb)
                    nkey = (ns, nb)
                    nd = d + cost
                    if nd < dist.get(nkey, float('inf')):
                        dist[nkey] = nd
                        heapq.heappush(pq, (nd, nkey))
    return best


@dataclass
class EquivExtractConfig(Config):
    maxv: int = 13
    add_budget: int = 3
    mul_budget: int = 1
    sub_budget: int = 1
    add_costs: tuple = (1, 2, 3)
    sub_costs: tuple = (1, 2, 3)
    mul_costs: tuple = (2, 3, 4, 5)
    inst_cap: int = 6

    def apply_difficulty(self, level):
        self.maxv = stochastic_rounding(13 + 3 * level)
        self.add_budget = stochastic_rounding(3 + level // 2)
        self.mul_budget = stochastic_rounding(1 + level // 2)
        self.sub_budget = stochastic_rounding(1 + level // 3)
        self.inst_cap = stochastic_rounding(6 + level // 2)


class RecursiveEquivalenceExtraction(Task):
    summary = ("Choose finite representatives from mutually recursive equivalence classes "
               "with alternative operators, shared subterms and operator budgets; return a "
               "minimum-cost acyclic expression with sharing counted once.")
    config_cls = EquivExtractConfig

    def generate_entry(self):
        cfg = self.config
        leaves = [0]
        if cfg.maxv >= 1:
            leaves.append(1)
        leaves = sorted(set(leaves))
        for _ in range(_MAX_ATTEMPTS):
            target = random.randint(2, cfg.maxv)
            ca = random.choice(cfg.add_costs)
            cs = random.choice(cfg.sub_costs)
            cm = random.choice(cfg.mul_costs)
            budgets = (cfg.add_budget, cfg.sub_budget, cfg.mul_budget)
            opdefs = make_opdefs((ca, cs, cm), budgets, cfg.maxv)
            mc = min_cost(leaves, target, opdefs, cfg.maxv, cfg.inst_cap)
            if mc is None or mc <= 0:
                continue
            surface = {target, cfg.maxv} | set(leaves)
            surface.update([ca, cs, cm, cfg.add_budget, cfg.sub_budget, cfg.mul_budget])
            if mc in surface:
                continue
            opspec = [{
                'op': nm,
                'cost': opdefs[nm][0],
                'budget': opdefs[nm][1],
            } for nm in ORDER]
            return Entry(
                metadata={
                    'atoms': leaves,
                    'maxv': int(cfg.maxv),
                    'target': int(target),
                    'operators': opspec,
                    'min_cost': int(mc),
                },
                answer=str(int(mc)),
            )
        raise RuntimeError("could not generate feasible instance")

    def render_prompt(self, metadata):
        atoms = metadata['atoms']
        maxv = metadata['maxv']
        target = metadata['target']
        op_line = "; ".join(
            "%s (cost %d, at most %d uses)" % (o['op'], o['cost'], o['budget'])
            for o in metadata['operators']
        )
        return (
            "A set of mutually recursive equivalence classes of expressions denotes integer "
            "values. To represent a value you start from the atom values %s (always available, "
            "free) and repeatedly combine two already-known values with an operator, keeping "
            "every intermediate result so any value may be reused by later steps at no extra "
            "cost (shared subterms count once). Each operator has a cost per use and a budget "
            "on how many times it may be used in total: %s. All values, including every "
            "intermediate, must stay between 0 and %d inclusive. Your goal is to represent the "
            "value %d. What is the minimum total cost (summing each distinct operator use once) "
            "of a valid representation? The answer is one integer."
            % (atoms, op_line, maxv, target)
        )

    def score_answer(self, answer, entry):
        try:
            val = int(str(answer).strip())
        except Exception:
            return 0.0
        return 1.0 if val == int(entry.metadata['min_cost']) else 0.0
