import math
import random
from dataclasses import dataclass
from functools import lru_cache

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'topological_sort_count (draw 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_novel_composition_r1/topological_sort_count',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}

design_choice = ("Generate instances from series-parallel posets with explicit SP-tree "
                 "descriptions, where the solver must reconstruct the poset and count "
                 "extensions via recursive composition formulas.")


def _comb(n, k):
    return math.comb(n, k)


def _sp_count(node):
    """Return (number_of_linear_extensions, number_of_elements) for an SP-tree node.

    Leaves are singletons. 'S' (series) forces every element of the left child before
    every element of the right; 'P' (parallel) leaves the two children incomparable.
    """
    if node[0] == 'L':
        return 1, 1
    op, left, right = node
    cl, sl = _sp_count(left)
    cr, sr = _sp_count(right)
    if op == 'S':
        return cl * cr, sl + sr
    return cl * cr * _comb(sl + sr, sl), sl + sr


def _sp_to_poset(node):
    """Map an SP-tree to (elements, set of strict relations) as (a, b) meaning a < b.

    Elements are freshly remapped to 0..n-1 in left-to-right leaf order.
    """
    elements = []
    rels = set()

    def rec(node):
        if node[0] == 'L':
            idx = len(elements)
            elements.append(idx)
            return [idx]
        op, left, right = node
        left_els = rec(left)
        right_els = rec(right)
        if op == 'S':
            for a in left_els:
                for b in right_els:
                    rels.add((a, b))
        return left_els + right_els

    rec(node)
    return list(elements), rels


def _count_linear_extensions_by_ideals(rels, n):
    """Independent verifier: count linear extensions by DP over down-closed ideals."""
    preds = [[] for _ in range(n)]
    for a, b in rels:
        preds[b].append(a)
    @lru_cache(maxsize=None)
    def go(mask):
        if mask == (1 << n) - 1:
            return 1
        total = 0
        # elements not yet placed that have all predecessors placed -> maximal in complement
        for x in range(n):
            if mask & (1 << x):
                continue
            if all(mask & (1 << p) for p in preds[x]):
                total += go(mask | (1 << x))
        return total
    return go(0)


def _render_sp(node):
    if node[0] == 'L':
        return str(node[1])
    op, left, right = node
    sym = '->' if op == 'S' else '|'
    return f"({_render_sp(left)} {sym} {_render_sp(right)})"


def _build_tree(target, op_limit_ratio):
    """Build a binary SP tree with exactly `target` leaves.

    op_limit_ratio in (0,1] biases the horizontal/vertical use of 'P'/'S'.  The tree is
    guaranteed (by resampling) to contain at least one 'P' node whenever target >= 3, so a
    full chain (count == 1) is never produced and the label set stays diverse.
    """
    counter = [0]

    def leaf():
        v = counter[0]
        counter[0] += 1
        return ('L', v)

    for _attempt in range(400):
        counter[0] = 0

        def rec(k):
            if k == 1:
                return leaf()
            a = random.randint(1, k - 1)
            b = k - a
            op = 'P' if random.random() < op_limit_ratio else 'S'
            return (op, rec(a), rec(b))

        tree = rec(target)
        if not _has_parallel(tree) and target >= 3:
            continue
        # Relabel the leaves with a uniform random permutation of 0..n-1 so that the
        # rendered expression is not tied to a fixed left-to-right label ordering.  The
        # extension count depends only on the poset structure, so any relabeling is safe
        # and it multiplies the pool of distinct instances by n!.
        perm = random.sample(range(target), target)
        tree = _relabel(tree, perm)
        return tree
    raise RuntimeError("failed to build a varied SP tree")


def _relabel(node, perm):
    if node[0] == 'L':
        return ('L', perm[node[1]])
    return (node[0], _relabel(node[1], perm), _relabel(node[2], perm))


def _has_parallel(node):
    if node[0] == 'L':
        return False
    return node[0] == 'P' or _has_parallel(node[1]) or _has_parallel(node[2])


@dataclass
class TopologicalSortCountV2Config(Config):
    min_leaves: int = 3
    max_leaves: int = 4
    op_limit_ratio: float = 0.5

    def apply_difficulty(self, level):
        self.min_leaves = 3 + (level * 3) // 4
        self.max_leaves = 5 + (level * 3) // 2
        self.op_limit_ratio = 0.5


class TopologicalSortCount(Task):
    summary = ("Count linear extensions of a finite poset or DAG using recursive "
               "decomposition or dynamic programming over ideals; ranges over width, "
               "height, series-parallel structure, and diamond patterns; answer is the "
               "exact count.")
    config_cls = TopologicalSortCountV2Config
    task_version = 2

    def generate_entry(self):
        while True:
            leaves = random.randint(self.config.min_leaves, self.config.max_leaves)
            tree = _build_tree(leaves, self.config.op_limit_ratio)
            expr = _render_sp(tree)
            count, n = _sp_count(tree)
            elements, rels = _sp_to_poset(tree)
            # Independent verification through general ideal-DP; reject if it disagrees
            # or if the count leaves the mathematically forced domain.
            expect = _count_linear_extensions_by_ideals(rels, n)
            if expect == count and count >= 1:
                break
        metadata = {
            "sp_expression": expr,
            "elements": n,
            "op_limit_ratio": float(self.config.op_limit_ratio),
            "count": int(count),
        }
        return Entry(metadata=metadata, answer=str(count))

    def render_prompt(self, metadata):
        return (
            "A series-parallel poset is built from its distinct elements. In the "
            "expression, 'A -> B' means series composition: every element of A must come "
            "before every element of B. 'A | B' means parallel composition: elements of A "
            "and B are mutually incomparable. Leaves are single elements. "
            f"Given this SP expression: {metadata['sp_expression']}  "
            "How many linear extensions (topological orders) does the poset have? "
            "Answer with a single nonnegative integer."
        )

    def score_answer(self, answer, entry):
        try:
            value = int(str(answer).strip())
        except (TypeError, ValueError):
            return 0.0
        reference = int(str(entry['answer']).strip())
        return 1.0 if value == reference else 0.0
