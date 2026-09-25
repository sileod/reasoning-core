"""Value-of-information (expected net value of an experiment) task.

A decision maker must commit to one action; the payoff of every action depends
on an unknown state of the world with a known prior. Without any test, the best
action maximises expected payoff. Each candidate experiment partitions the
states into mutually exclusive outcomes, has prior probabilities per outcome,
and has a cost. The expected value with information is, for each outcome, the
best expected payoff under that outcome's posterior, averaged over outcomes.
The expected net value of an experiment is that posterior-optimal value minus
the no-test optimal value minus the test cost. The solver returns the name of
the experiment with the highest expected net value, breaking ties by name.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class InterventionInfoConfig(Config):
    num_states: int = 3
    num_actions: int = 3
    num_experiments: int = 3
    outcomes_per_experiment: int = 2

    def apply_difficulty(self, level):
        self.num_states = 3 + level
        self.num_actions = 2 + level
        self.num_experiments = 3
        self.outcomes_per_experiment = 2 + level // 2


_NAMES = ["Amber", "Beryl", "Cobalt", "Dune", "Echo", "Fern"]


def _scaled_prior_value(counts, payoffs):
    """Best expected payoff under the prior, scaled by the total count."""
    total = sum(counts)
    best = None
    for a in payoffs:
        val = sum(cnt * rew for cnt, rew in zip(counts, a))
        if best is None or val > best:
            best = val
    return best


def _scaled_info_value(counts, payoffs, groups):
    """Scaled expected best payoff after observing the outcome (a partition)."""
    val = 0
    for group in groups:
        gbest = None
        for a in payoffs:
            s = sum(counts[i] * a[i] for i in group)
            if gbest is None or s > gbest:
                gbest = s
        val += gbest
    return val


def _build_instance(cfg):
    ns, na, ne = cfg.num_states, cfg.num_actions, cfg.num_experiments
    op = cfg.outcomes_per_experiment
    for _ in range(500):
        states = list(range(ns))
        counts = [random.randint(1, 6) for _ in states]
        payoffs = [
            [random.randint(-9, 12) for _ in states] for _ in range(na)
        ]
        total = sum(counts)
        prior_val = _scaled_prior_value(counts, payoffs)

        names = random.sample(_NAMES, ne)
        experiments = []
        best_net = None
        best_name = None
        for name in names:
            if op > ns:
                continue
            groups = _random_partition(states, op)
            cost = random.randint(0, 8)
            info_val = _scaled_info_value(counts, payoffs, groups)
            net = info_val - prior_val - cost * total
            experiments.append({
                "name": name,
                "cost": cost,
                "outcomes": [sorted(g) for g in groups],
                "prior_probabilities": [
                    sum(counts[i] for i in g) for g in groups
                ],
                "net_value": net,
            })
            if best_net is None or net > best_net or (net == best_net and name < best_name):
                best_net = net
                best_name = name
        if len(experiments) < 2:
            continue
        return states, counts, payoffs, prior_val, experiments, best_name, best_net
    raise RuntimeError("could not build intervention instance")


def _random_partition(states, k):
    random.shuffle(states)
    group_sizes = []
    remaining = len(states)
    for j in range(k - 1):
        # each group gets at least one element, keep the last groups feasible
        max_here = remaining - (k - 1 - j)
        size = random.randint(1, max_here)
        group_sizes.append(size)
        remaining -= size
    group_sizes.append(remaining)
    groups, idx = [], 0
    for size in group_sizes:
        groups.append(states[idx:idx + size])
        idx += size
    return groups


class InterventionInformationValue(Task):
    summary = ("Compare experiments that reveal uncertain intervention "
               "responses before a consequential choice; combine likelihoods, "
               "posterior-optimal actions, and test costs to return the name "
               "of the experiment with the highest expected net value (bag the "
               "expected best payoff under each outcome's posterior, subtract "
               "the no-test best expected payoff and the test cost).")
    design_choice = ("Represent experiments as sets of possible intervention "
                     "outcomes with prior probabilities; solver returns the "
                     "experiment name with highest expected net value, "
                     "computed via posterior action regret minus test cost.")
    config_cls = InterventionInfoConfig

    def generate_entry(self):
        cfg = self.config
        (states, counts, payoffs, prior_val,
         experiments, best_name, best_net) = _build_instance(cfg)
        winner = next(e for e in experiments if e["name"] == best_name)
        assert winner["net_value"] == best_net
        for e in experiments:
            assert len(e["outcomes"]) == len(e["prior_probabilities"])
            assert all(p >= 1 for p in e["prior_probabilities"])
            covered = [i for g in e["outcomes"] for i in g]
            assert sorted(covered) == sorted(states)
        metadata = {
            "num_states": cfg.num_states,
            "counts": counts,
            "payoffs": payoffs,
            "prior_value": prior_val,
            "experiments": experiments,
            "answer_name": best_name,
            "answer_net": int(best_net),
        }
        return Entry(metadata=metadata, answer=str(best_name))

    def render_prompt(self, metadata):
        m = metadata
        lines = [
            "You must choose one action, but the reward each action yields "
            "depends on an unknown state of the world. The states are "
            "listed with their prior likelihood weights (relative to each "
            "other): %s."
            % ", ".join(
                "state %d has weight %d" % (i + 1, w)
                for i, w in enumerate(m["counts"])
            ),
            "",
            "The reward table below gives, for each action and each state, "
            "the reward of taking that action when that state is true "
            "(rows are actions, columns are states):",
            "",
        ]
        header = "Action | " + " | ".join("st%d" % (i + 1) for i in range(m["num_states"]))
        sep = "---" + "|---" * m["num_states"]
        rows = []
        for ai, a in enumerate(m["payoffs"]):
            rows.append("A%d | " % (ai + 1) + " | ".join(str(v) for v in a))
        lines.append("| " + header)
        lines.append("| " + sep)
        for r in rows:
            lines.append("| " + r)
        lines.append("")
        lines.append(
            "Before choosing, you may run exactly one experiment at its listed "
            "cost. Each experiment reveals which of its outcomes holds; the "
            "outcomes of an experiment are a partition of the states (each "
            "state belongs to exactly one outcome), and each outcome lists the "
            "states in it and its prior likelihood weight. Given an outcome, "
            "the state is one of the states in that outcome with posterior "
            "proportional to the prior weights."
        )
        lines.append("")
        for e in m["experiments"]:
            out_desc = "; ".join(
                "outcome %d (prior weight %d) contains states %s" % (
                    j + 1, e["prior_probabilities"][j],
                    ", ".join("st%d" % (i + 1) for i in e["outcomes"][j]),
                )
                for j in range(len(e["outcomes"]))
            )
            lines.append(
                "Experiment %s costs %d: %s."
                % (e["name"], e["cost"], out_desc)
            )
        lines.append("")
        lines.append(
            "Compute the expected value of information for each experiment: "
            "for every outcome, take the best expected reward under that "
            "outcome's posterior distribution, then average those best "
            "rewards over the outcomes weighted by their prior, and subtract "
            "the best expected reward achievable with no test and the "
            "experiment's cost. Return the name of the experiment (Amber, "
            "Beryl, Cobalt, ...) with the highest expected net value; if "
            "two tie, the one whose name comes first alphabetically. Give "
            "only the experiment name as your answer."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        a = str(answer).strip()
        if a == entry.answer:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'intervention_information_value (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/intervention_information_value',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
