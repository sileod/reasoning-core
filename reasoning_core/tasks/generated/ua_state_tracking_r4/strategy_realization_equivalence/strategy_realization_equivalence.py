"""Translation of decision-plan mixtures into decision-history weights.

A full binary decision tree of depth ``n``; the all-Left decision history is the
path obtained by always branching Left. Each of the ``n`` levels contributes one
node on that path. A chance node makes nature branch Left with a stated
probability p; a decision node applies the agent's policy, which either commits
to Left (a complete-plan step, probability 1), commits to Right (making the
branch unreachable, probability 0), or makes a local random choice taking Left
with a stated probability q. The realization probability of the all-Left history
is the product of the Left probabilities down the path. Two policy mixtures are
equivalent exactly when they yield the same reduced fraction after unreachable
branches are pruned.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


CHANCE_POOL = [
    Fraction(1, 2), Fraction(1, 3), Fraction(2, 3),
    Fraction(1, 4), Fraction(3, 4), Fraction(1, 5),
    Fraction(2, 5), Fraction(3, 5), Fraction(4, 5),
]
RANDOM_POOL = [
    Fraction(1, 2), Fraction(1, 3), Fraction(2, 3),
    Fraction(1, 4), Fraction(3, 4),
]

RIGHT_PROB = 0.10
Q_PROB = 0.40


def _fmt(f):
    return str(f) if f.denominator != 1 else f"{f.numerator}"


def _to_frac(value):
    text = str(value).strip()
    if text in ("0", "0/1"):
        return Fraction(0, 1)
    try:
        frac = Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None
    if frac.denominator <= 0:
        return None
    return frac


@dataclass
class StrategyRealizationEquivalenceConfig(Config):
    max_depth: int = 2

    def apply_difficulty(self, level):
        self.max_depth = 2 + level


class StrategyRealizationEquivalence(Task):
    """Grouping under ua_state_tracking_r4 (trial module)."""

    summary = (
        "Translate a mixture of complete-plan steps and local random choices on a "
        "chance-node binary decision tree into the reduced-fraction probability "
        "weight of the all-Left history, pruning Right-committed nodes as "
        "unreachable, so equivalent policy mixtures agree on one canonical fraction."
    )
    design_choice = (
        "Represent plans as decision trees with chance nodes; solvers output a "
        "canonical fraction for equivalence, with unreachable branches pruned "
        "before comparison."
    )
    config_cls = StrategyRealizationEquivalenceConfig

    def generate_entry(self):
        depth = self.config.max_depth

        n_chance = random.randint(1, depth)
        chance_pos = set(random.sample(range(depth), n_chance))

        nodes = []
        has_right = False
        for i in range(depth):
            if i in chance_pos:
                nodes.append(("chance", random.choice(CHANCE_POOL)))
                continue
            r = random.random()
            if r < RIGHT_PROB and not has_right:
                nodes.append(("right", 0))
                has_right = True
            elif r < RIGHT_PROB + Q_PROB:
                nodes.append(("q", random.choice(RANDOM_POOL)))
            else:
                nodes.append(("left", 1))

        contributing = sum(1 for kind, _ in nodes if kind in ("chance", "q"))
        if contributing < 2:
            for i, (kind, _value) in enumerate(nodes):
                if kind in ("left", "right") and contributing < 2:
                    nodes[i] = ("q", random.choice(RANDOM_POOL))
                    contributing += 1

        prob = Fraction(1, 1)
        unreachable = False
        for kind, value in nodes:
            if kind == "chance":
                prob *= value
            elif kind == "q":
                prob *= value
            elif kind == "right":
                unreachable = True

        if unreachable:
            prob = Fraction(0, 1)

        assert isinstance(prob, Fraction)
        assert prob.denominator > 0
        assert Fraction(0, 1) <= prob <= Fraction(1, 1)

        gold = _fmt(prob)
        labels = []
        for kind, value in nodes:
            if kind == "chance":
                labels.append(f"chance {_fmt(value)}")
            elif kind == "left":
                labels.append("decision left")
            elif kind == "q":
                labels.append(f"decision q {_fmt(value)}")
            else:
                labels.append("decision right")

        return Entry(
            metadata={"n": depth, "nodes": labels, "gold": gold},
            answer=gold,
        )

    def render_prompt(self, metadata):
        depth = metadata["n"]
        lines = "\n".join(
            f"{i + 1}. {node}" for i, node in enumerate(metadata["nodes"])
        )
        return (
            f"A sequential decision problem is modeled as a full binary decision "
            f"tree of depth {depth}. Consider the all-Left decision history, the "
            f"path obtained by always branching Left; each of the {depth} levels "
            f"contributes one node on this path, listed top-down:\n\n"
            f"{lines}\n\n"
            f"At a chance node, nature branches Left with the stated probability "
            f"and Right otherwise. At a decision node, the agent's plan either "
            f"commits to Left, commits to Right, or makes a local random choice "
            f"taking Left with the stated probability q. Compute the realization "
            f"probability of the all-Left history: the product of the Left-branch "
            f"probabilities at every level. Give the answer as a single reduced "
            f"fraction \"a/b\" with b > 0, or \"0\" if the history is unreachable "
            f"because some node commits to Right."
        )

    def score_answer(self, answer, entry):
        gold = _to_frac(entry["answer"])
        if gold is None:
            return 0
        got = _to_frac(answer)
        if got is None:
            return 0
        return 1 if got == gold else 0


TASK_META = {'parent_source_id': None,
 'idea': 'strategy_realization_equivalence (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/strategy_realization_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
