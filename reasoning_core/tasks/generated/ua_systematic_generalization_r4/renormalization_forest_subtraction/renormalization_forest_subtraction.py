"""Renormalization forest subtraction.

Zimmermann-style forest subtraction on integer divergence forests: each node
carries an integer weight; divergent nodes additionally carry a modulus that
defines their singular-part projection.  A node's bare value equals its weight
plus the renormalized values of its nested children, combined additively so a
single branch cannot collapse the whole result.  At a divergent node the
singular part (the submultiple of the modulus left by integer division) is
projected out, leaving the finite remainder; the forest total is the sum over
the disjoint top-level trees.  Nested divergences are consumed by the
recursion, disjoint ones combine by addition, and overlapping choices are
never subtracted twice.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'renormalization_forest_subtraction (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/renormalization_forest_subtraction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1339177894,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class RenormForestConfig(Config):
    num_trees: int = 2
    max_depth: int = 2
    weight_hi: int = 3
    modulus_hi: int = 3
    div_prob: float = 0.6
    branch_hi: int = 1

    def apply_difficulty(self, level):
        self.num_trees = 2 + (level >= 4) + (level >= 6)
        self.max_depth = 2 + level // 3
        self.branch_hi = 1 + (level >= 2) + (level >= 5)
        self.weight_hi = 3 + level
        self.modulus_hi = 3 + level


def _renorm_node(node):
    weight, mod, div, kids = node
    inner = 0
    for kid in kids:
        inner += _renorm_node(kid)
    bare = weight + inner
    if div:
        return bare % mod
    return bare


def renorm_forest(forest):
    total = 0
    for root in forest:
        total += _renorm_node(root)
    return total


def _build_subtree(cfg, depth_left):
    if depth_left <= 0:
        return None
    weight = random.randint(1, cfg.weight_hi)
    div = random.random() < cfg.div_prob
    mod = None
    if div:
        mod = random.randint(2, cfg.modulus_hi)
    kids = []
    if depth_left > 1:
        nk = random.randint(0, cfg.branch_hi)
        for _ in range(nk):
            sub = _build_subtree(cfg, depth_left - 1)
            if sub is not None:
                kids.append(sub)
    return [weight, mod, div, kids]


def _build_forest(cfg):
    n = random.randint(cfg.num_trees, cfg.num_trees + 1)
    forest = []
    for _ in range(n):
        root = _build_subtree(cfg, cfg.max_depth)
        if root is not None:
            forest.append(root)
    return forest


class RenormalizationForestSubtraction(Task):
    summary = ("Subtract divergent substructures via a supplied singular-part "
               "projection; combine nested and disjoint subtraction forests while "
               "excluding overlapping choices, returning a counterterm or "
               "renormalized expression.")
    config_cls = RenormForestConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        forest = _build_forest(cfg)
        answer = renorm_forest(forest)
        assert isinstance(answer, int) and answer >= 0, answer
        assert renorm_forest(forest) == answer
        metadata = {"forest": forest}
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        lines = [
            "You are renormalizing a forest of divergent substructures by "
            "forest subtraction.",
            "Each node is written as [weight] for a finite substructure, or as "
            "[weight|modulus] for a divergent one; nested children are listed "
            "between parentheses ( ) and separated by commas.",
            "A node's bare value is its weight plus the renormalized values of "
            "all its children. The singular-part projection of a divergent node "
            "is the part of its bare value that is an exact whole multiple of "
            "its modulus; renormalizing that node subtracts that singular part, "
            "leaving the finite remainder bare value modulo the modulus. Finite "
            "nodes are taken as their bare value.",
            "Nested divergences are consumed by this recursion and disjoint "
            "divergences combine by addition, so overlapping choices are never "
            "subtracted twice.",
            "The forest's total renormalized value is the sum of the "
            "renormalized values of its top-level trees.",
        ]
        rendered = " , ".join(_render_node(root) for root in metadata["forest"])
        lines.append("Forest: " + rendered)
        lines.append("What is the total renormalized value? Answer with one "
                     "non-negative integer.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return _score(answer, entry)


def _render_node(node):
    weight, mod, div, kids = node
    if div:
        s = "[%d|%d]" % (weight, mod)
    else:
        s = "[%d]" % weight
    if kids:
        s += "(" + " , ".join(_render_node(k) for k in kids) + ")"
    return s


def _score(answer, entry):
    if answer is None:
        return 0.0
    try:
        val = int(str(answer).strip())
    except (TypeError, ValueError):
        return 0.0
    forest = entry["metadata"]["forest"] if isinstance(entry, dict) else entry.metadata["forest"]
    expected = renorm_forest(forest)
    return 1.0 if val == expected else 0.0
