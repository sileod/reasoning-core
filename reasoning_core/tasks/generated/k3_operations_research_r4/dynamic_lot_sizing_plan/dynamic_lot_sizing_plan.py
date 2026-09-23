import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class DynamicLotSizingConfig(Config):
    horizon: int = 5
    max_setup: int = 14
    max_holding: int = 5
    max_demand: int = 8

    def apply_difficulty(self, level):
        self.horizon = 5 + level
        self.max_setup = 14 + 4 * level
        self.max_holding = 5 + (level + 1) // 2
        self.max_demand = 8 + level


def _plan_cost(prod_set, demands, setup, holding):
    horizon = len(demands)
    prod = sorted(prod_set)
    prodset = set(prod)
    boundaries = prod + [horizon]
    blocks = {}
    for bi, a in enumerate(prod):
        blocks[a] = sum(demands[a:boundaries[bi + 1]])
    in_stock = 0
    total = 0
    for t in range(horizon):
        if t in prodset:
            in_stock += blocks[t]
        in_stock -= demands[t]
        if in_stock < 0:
            return None
        total += holding * in_stock
    total += setup * len(prod)
    return total


def _all_optimal_plans(demands, setup, holding):
    horizon = len(demands)
    plans = []
    best_cost = None
    for r in range(1, horizon + 1):
        for prod in itertools.combinations(range(horizon), r):
            cost = _plan_cost(prod, demands, setup, holding)
            if cost is None:
                continue
            if best_cost is None or cost < best_cost:
                best_cost = cost
                plans = [list(prod)]
            elif cost == best_cost:
                plans.append(list(prod))
    return plans, best_cost


class DynamicLotSizingPlan(Task):
    summary = "Plan production over a horizon with setup and holding costs: a forward pass weighs producing now against carrying stock from an earlier setup; answers are production periods, minimal cost, or stock crossing a given boundary."
    design_choice = "Answer as the set of production periods achieving minimal cost, with instances generated so multiple optimal plans exist and the solver must return the lexicographically smallest one."
    config_cls = DynamicLotSizingConfig

    def generate_entry(self):
        horizon = self.config.horizon
        setup = self.config.max_setup
        holding = self.config.max_holding
        max_demand = self.config.max_demand
        while True:
            demands = [random.randint(1, max_demand) for _ in range(horizon)]
            for _ in range(10):
                demands[random.randrange(horizon)] = random.randint(0, max_demand)
            plans, _ = _all_optimal_plans(demands, setup, holding)
            if len(plans) < 2:
                continue
            best = min(plans)
            if len(best) < 2:
                continue
            if any(demands[t] == 0 for t in best):
                continue
            break
        return Entry(
            metadata={
                "horizon": horizon,
                "demands": demands,
                "setup": setup,
                "holding": holding,
                "answer": best,
            },
            answer=" ".join(str(t) for t in best),
        )

    def render_prompt(self, metadata):
        d = metadata
        return (
            f"Over a horizon of {d['horizon']} periods, demand per period is "
            f"{d['demands']}. Starting a production run in any period costs a fixed "
            f"setup cost of {d['setup']}; once a run is started, its produced units "
            f"cover that period and every later period until the next run. A unit of "
            f"stock held from one period into the next costs {d['holding']}; demand in "
            f"a period with no production must be met from earlier stock and cannot be "
            f"backlogged. Find the set of production periods (space-separated integers, "
            f"0-indexed) achieving the minimal total cost; if several plans tie, give "
            f"the lexicographically smallest one, e.g. '0 3'."
        )

    def score_answer(self, answer, entry):
        if isinstance(answer, str):
            norm = answer.strip()
            if not norm:
                return 0.0
            return 1.0 if norm == entry.answer else 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'dynamic_lot_sizing_plan (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/dynamic_lot_sizing_plan',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
