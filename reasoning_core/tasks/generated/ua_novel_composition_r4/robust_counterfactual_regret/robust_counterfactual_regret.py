import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'robust_counterfactual_regret (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_novel_composition_r4/robust_counterfactual_regret',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4238614268,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def worst_regret(costs):
    I = len(costs)
    S = len(costs[0]) if I else 0
    regret = [[0] * S for _ in range(I)]
    for s in range(S):
        best = min(costs[i][s] for i in range(I))
        for i in range(I):
            regret[i][s] = costs[i][s] - best
    return regret


def best_intervention_and_witness(costs):
    I = len(costs)
    S = len(costs[0]) if I else 0
    regret = worst_regret(costs)
    worst = [max(row) for row in regret]
    bi = min(range(I), key=lambda i: worst[i])
    ws = min(range(S), key=lambda s: -regret[bi][s])
    return bi, ws, worst[bi], regret


@dataclass
class RegretConfig(Config):
    num_interventions: int = 3
    num_scenarios: int = 2
    max_cost: int = 4

    def apply_difficulty(self, level):
        self.num_interventions = 3 + level
        self.num_scenarios = 2 + level
        self.max_cost = 4 + 3 * level


class RobustCounterfactualRegret(Task):
    summary = "Compare interventions across coupled uncertainty scenarios, measuring each loss against the best alternative in that same scenario; return the minimum-worst-regret intervention or its adversarial witness."
    config_cls = RegretConfig

    def generate_entry(self):
        I = self.config.num_interventions
        S = self.config.num_scenarios
        while True:
            costs = [
                [random.randint(0, self.config.max_cost) for _ in range(S)]
                for _ in range(I)
            ]
            bi, ws, worst_val, _ = best_intervention_and_witness(costs)
            if not (isinstance(worst_val, int) and worst_val >= 0):
                continue
            return Entry(
                metadata={
                    "costs": costs,
                    "num_interventions": I,
                    "num_scenarios": S,
                    "best_intervention": bi,
                    "witness_scenario": ws,
                    "worst_regret": worst_val,
                },
                answer=f"{bi} {ws}",
            )

    def render_prompt(self, metadata):
        costs = metadata["costs"]
        rows = []
        for i, row in enumerate(costs):
            cells = ", ".join(str(c) for c in row)
            rows.append(f"  intervention {i}: [{cells}]")
        table = "\n".join(rows)
        return (
            f"An agent must pick one intervention to use in all scenarios, hedging against "
            f"unknown future conditions. There are {metadata['num_interventions']} interventions "
            f"and {metadata['num_scenarios']} coupled scenarios, where entry cost[i][s] is the loss "
            f"of intervention i under scenario s:\n{table}\n"
            f"Use Savage minimax regret. For each scenario, an intervention's regret is its loss "
            f"minus the best (minimum) loss among all interventions in that same scenario; an "
            f"intervention's worst-case regret is the maximum of its regrets over scenarios. The "
            f"robust intervention is the one with the smallest worst-case regret (ties: smallest "
            f"index). Its adversarial witness is the scenario that gives it its worst-case regret "
            f"(ties: smallest scenario index). "
            f"Answer as \"<robust intervention index> <witness scenario index>\"."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        want = f"{entry.metadata['best_intervention']} {entry.metadata['witness_scenario']}"
        return 1.0 if str(answer).strip() == want else 0.0
