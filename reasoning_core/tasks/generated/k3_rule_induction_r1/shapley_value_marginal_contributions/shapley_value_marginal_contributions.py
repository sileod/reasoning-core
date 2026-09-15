import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'shapley_value_marginal_contributions (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_rule_induction_r1/shapley_value_marginal_contributions',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Present the value map as a lookup table and require the solver to compute the Shapley value vector as a list of reduced fractions, with player labels given as integers."


@dataclass
class ShapleyConfig(Config):
    players: int = 3
    value_range: int = 10

    def apply_difficulty(self, level):
        self.players = min(3 + level, 6)
        self.value_range = 5 + 3 * level


class ShapleyValueMarginalContributions(Task):
    summary = "For small coalitional value functions over varied player sets and value maps, average each player's marginal contribution across all permutations to return the exact rational Shapley value vector."
    config_cls = ShapleyConfig

    def generate_entry(self):
        n = self.config.players
        from math import factorial
        subsets = list(range(1 << n))
        value = {}
        for mask in subsets:
            value[mask] = random.randint(0, self.config.value_range)
        sh = [Fraction(0) for _ in range(n)]
        denom = factorial(n)
        for i in range(n):
            for mask in range(1 << n):
                if mask & (1 << i):
                    continue
                k = bin(mask).count("1")
                coeff = Fraction(factorial(k) * factorial(n - k - 1), denom)
                sh[i] += coeff * (value[mask | (1 << i)] - value[mask])
        full_mask = (1 << n) - 1
        expected_sum = value[full_mask] - value[0]
        if sum(sh) != expected_sum:
            raise RuntimeError("Shapley values do not sum to v(full)-v(empty)")
        for v in sh:
            if not (-self.config.value_range <= v <= self.config.value_range):
                raise RuntimeError("Shapley value out of domain")
        ans = " ".join(str(f) for f in sh)
        return Entry(metadata={
            "n": n,
            "value_map_rows": [[mask, value[mask]] for mask in sorted(value)],
            "players_ints": list(range(n)),
            "shapley": [str(f) for f in sh],
        }, answer=ans)

    def render_prompt(self, metadata):
        n = metadata["n"]
        rows = "\n".join(f"   subset {mask}: value {val}" for mask, val in metadata["value_map_rows"])
        return (
            f"A coalitional game has players labeled 0..{n-1}. The value map gives the value v(S) "
            f"for each subset S (represented by its bit-mask of players included):\n{rows}\n"
            f"Compute the Shapley value vector, where player i's Shapley value is the average of its "
            f"marginal contribution v(S u {{i}}) - v(S) over all random orders of the players.\n"
            f"Give the answer as the list of reduced fractions for players 0..{n-1}, space-separated, "
            f"e.g. for 3 players '3/2 1/2 5/2'."
        )

    def score_answer(self, answer, entry):
        try:
            given = [Fraction(s.strip()) for s in answer.strip().split()]
        except Exception:
            return 0.0
        gold = [Fraction(s) for s in entry.metadata["shapley"]]
        if len(given) != len(gold):
            return 0.0
        return 1.0 if all(g == h for g, h in zip(given, gold)) else 0.0
