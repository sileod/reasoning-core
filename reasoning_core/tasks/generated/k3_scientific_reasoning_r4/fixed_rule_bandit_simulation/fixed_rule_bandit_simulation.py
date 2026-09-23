"""Simulate a multi-armed bandit allocation policy over tabulated reward streams.

Three deterministic allocation rules are supported -- epsilon-greedy on a fixed
exploration schedule, UCB with a given constant c, and Thompson sampling over a
tabulated grid of posterior draws.  The solver must track every arm's pull count
and report the total pulls of the least-pulled arm, so no single arm can dominate
the reasoning.

All rewards are tabulated 0/1 success streams keyed by pull ordinal.  Every tie is
broken toward the smallest arm index, and the answer (a non-negative integer, the
minimum pull count across arms) is well defined even when the least-pulled arm is
not unique.
"""

import math
import random
from dataclasses import dataclass

from scipy.stats import beta as _beta

from reasoning_core.template import Config, Entry, Task


def _build_grid(n=64, seed=1013):
    rng = random.Random(seed)
    # Rounded to 3 decimals so the value printed in the prompt is exactly the value
    # the simulation consumes; a solver that reads the grid off the prompt therefore
    # reproduces the same draws bit for bit.
    return [round(0.5 + 0.5 * rng.random(), 3) for _ in range(n)]


# A fixed, deterministic tabulated grid of (0,1) draws built once at import with a
# literal seed.  Because the values are printed verbatim in the prompt whenever the
# Thompson policy is used, they are part of the instance the solver sees, never a
# hidden author-side constant.
_GRID = _build_grid()


def _beta_ppf(u, alpha, beta):
    eps = 1e-9
    return _beta.ppf(min(max(u, eps), 1.0 - eps), alpha, beta)


def _simulate(n_arms, rounds, streams, policy, explore_step, ucb_c):
    """Run one bandit simulation; return (success_counts, pull_counts, choices)."""
    succ = [0] * n_arms
    pull = [0] * n_arms
    choices = []
    for r in range(1, rounds + 1):
        if policy == "epsilon":
            if r % explore_step == 0:
                # Exploration: pull the least-pulled arm, smallest index on tie.
                target = min(range(n_arms), key=lambda i: (pull[i], i))
            else:
                # Exploit the highest empirical success rate; unpulled -> -inf.
                vals = [(-1e18 if pull[i] == 0 else succ[i] / pull[i]) for i in range(n_arms)]
                target = min(range(n_arms), key=lambda i: (-vals[i], i))
        elif policy == "ucb":
            vals = []
            for i in range(n_arms):
                if pull[i] == 0:
                    vals.append(float("inf"))
                else:
                    vals.append(succ[i] / pull[i] + ucb_c * math.sqrt(math.log(r) / pull[i]))
            target = min(range(n_arms), key=lambda i: (-vals[i], i))
        else:  # thompson
            vals = []
            for i in range(n_arms):
                u = _GRID[(i * 7 + r * 13) % len(_GRID)]
                alpha = 1 + succ[i]
                beta = 1 + (pull[i] - succ[i])
                vals.append(_beta_ppf(u, alpha, beta))
            target = min(range(n_arms), key=lambda i: (-vals[i], i))
        succ[target] += streams[target][pull[target]]
        pull[target] += 1
        choices.append(target)
    return succ, pull, choices


@dataclass
class FixedRuleBanditConfig(Config):
    n_arms: int = 3
    rounds_min: int = 12
    rounds_max: int = 24
    densities: tuple = (0.2, 0.5, 0.8)
    steps: tuple = (2, 3)
    ucbs: tuple = (0.5, 1.0, 1.5)

    def apply_difficulty(self, level):
        # Difficulty scales in both the number of arms and the total number of
        # rounds, so the least-pulled count spans an ever-widening range.
        self.n_arms = 3 + (level // 2)
        self.rounds_min = 12 + 6 * level
        self.rounds_max = 24 + 13 * level
        self.densities = (0.2, 0.5, 0.8)
        self.steps = (2, 3) if level < 2 else (3, 4)
        self.ucbs = (0.5, 1.0, 1.5)


class FixedRuleBanditSimulation(Task):
    summary = ("Simulate allocation policies - epsilon-greedy on a fixed schedule, UCB with a "
               "given c, Thompson over tabulated grids - on tabulated success streams with fixed "
               "tie-breaks; answer the least-pulled arm's total pull count.")
    design_choice = ("Vary the difficulty by asking for the least-pulled arm's total count, "
                     "forcing solvers to track all arms, not just the top one.")
    config_cls = FixedRuleBanditConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(400):
            policy = random.choice(("epsilon", "ucb", "thompson"))
            n_arms = cfg.n_arms
            rounds = random.randint(cfg.rounds_min, cfg.rounds_max)
            explore_step = random.choice(cfg.steps)
            ucb_c = random.choice(cfg.ucbs)
            densities = [random.choice(cfg.densities) for _ in range(n_arms)]
            streams = []
            for p in densities:
                streams.append([1 if random.random() < p else 0 for _ in range(rounds)])
            succ, pull, _choices = _simulate(
                n_arms, rounds, streams, policy, explore_step, ucb_c
            )
            min_pull = min(pull)
            if 1 <= min_pull <= rounds and min_pull < rounds:
                break
        else:
            raise RuntimeError("bandit simulation never produced an admissible draw")
        metadata = {
            "n_arms": int(n_arms),
            "rounds": int(rounds),
            "policy": policy,
            "explore_step": int(explore_step),
            "ucb_c": float(ucb_c),
            "streams": [[int(v) for v in s] for s in streams],
            "pull_counts": [int(p) for p in pull],
            "least_pulled_count": int(min_pull),
        }
        if policy == "thompson":
            metadata["grid"] = [float(v) for v in _GRID]
        assert sum(pull) == rounds
        assert all(0 <= c <= rounds for c in pull)
        assert 1 <= min_pull <= rounds
        return Entry(metadata=metadata, answer=str(min_pull))

    def render_prompt(self, metadata):
        policy = metadata["policy"]
        if policy == "epsilon":
            rule = (
                "Epsilon-greedy on a fixed schedule: the exploration rate is 1/%d, so on every "
                "round r that is a multiple of %d (r %% %d == 0) you EXPLORE by pulling the arm "
                "that has been pulled the fewest times so far; on all other rounds you EXPLOIT by "
                "pulling the arm with the highest empirical success rate (successes %s pulls before "
                "that round); an arm never pulled before is treated as having rate -infinity."
                % (metadata["explore_step"], metadata["explore_step"], metadata["explore_step"], "/")
            )
        elif policy == "ucb":
            rule = (
                "UCB with constant c=%.2f: at round r, each arm i that has already been pulled "
                "receives the value mean_i + c*sqrt(ln(r)/n_i), where n_i is its number of pulls "
                "and mean_i its empirical success rate before round r; an arm not yet pulled "
                "receives +infinity. Pull the arm with the largest value." % metadata["ucb_c"]
            )
        else:
            rule = (
                "Thompson sampling over tabulated Beta posteriors: each arm starts with a "
                "Beta(1,1) prior; after s successes and f failures its posterior is "
                "Beta(1+s, 1+f). At round r draw one sample for every arm from its current "
                "posterior, where the sample is the inverse-CDF of the posterior Beta evaluated "
                "at the tabulated grid value below whose slot is assigned deterministically by "
                "slot = (arm_index*7 + r*13) mod %d. Pull the arm whose drawn sample is largest."
                % len(_GRID)
            )
        lines = [
            "You are simulating a multi-armed bandit with %d arms labeled 0 through %d, over %d "
            "rounds (rounds 1..%d). Each arm i has a tabulated reward stream; on its j-th pull it "
            "returns stream_i[j] (1 = success, 0 = failure)."
            % (metadata["n_arms"], metadata["n_arms"] - 1, metadata["rounds"], metadata["rounds"]),
            "Reward streams:",
        ]
        for i, s in enumerate(metadata["streams"]):
            lines.append("arm %d: %s" % (i, ",".join(map(str, s))))
        lines.append("Allocation rule: " + rule)
        if policy == "thompson":
            lines.append(
                "Tabulated grid (index -> value): "
                + ",".join("%d:%s" % (i, _GRID[i]) for i in range(len(_GRID)))
            )
        lines.append(
            "Tie-break: whenever two or more arms tie for the arm the rule would choose, always "
            "pick the arm with the smallest index."
        )
        lines.append(
            "What is the total number of pulls received by the least-pulled arm at the end of "
            "round %d? Answer with a single integer." % metadata["rounds"]
        )
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'fixed_rule_bandit_simulation (variant 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/fixed_rule_bandit_simulation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
