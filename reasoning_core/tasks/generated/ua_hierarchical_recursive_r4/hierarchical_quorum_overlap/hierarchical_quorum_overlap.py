import ast
import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict


TASK_META = {'parent_source_id': None,
 'idea': 'hierarchical_quorum_overlap (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_hierarchical_recursive_r4/hierarchical_quorum_overlap',
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

INF = float('inf')

_PRIVATE_A = list('abcdefghij')
_PRIVATE_B = list('klmnopqrst')
_SHARED_NAMES = ['sx', 'sy', 'sz', 'sw', 'sv', 'su']


@dataclass
class HierarchicalQuorumOverlapConfig(Config):
    members: int = 3
    depth: int = 1
    shared_pool: int = 2

    def apply_difficulty(self, level):
        self.members = 3 + level
        self.depth = 1 + level // 3
        self.shared_pool = min(2 + level // 2, 4)


def _build_tree(members, depth):
    members = list(members)
    frac = round(random.uniform(0.4, 0.8), 2)
    if depth <= 1 or len(members) <= 1:
        return [frac] + members
    num_groups = random.randint(2, min(3, len(members)))
    random.shuffle(members)
    groups = [[] for _ in range(num_groups)]
    for i, m in enumerate(members):
        groups[i % num_groups].append(m)
    children = [_build_tree(g, depth - 1) for g in groups]
    return [frac] + children


def _leaf_set(node):
    if isinstance(node, str):
        return {node}
    result = set()
    for child in node[1:]:
        result |= _leaf_set(child)
    return result


def _frac(node):
    return node[0]


def _children(node):
    return node[1:]


def _satisfied(node, selected):
    if isinstance(node, str):
        return node in selected
    children = _children(node)
    m = len(children)
    need = math.ceil(_frac(node) * m)
    count = sum(1 for c in children if _satisfied(c, selected))
    return count >= need


def _mincost(node, forced, sharedset):
    if isinstance(node, str):
        if node in sharedset and node not in forced:
            return (INF, frozenset([node]))
        if node in forced:
            return (0, frozenset([node]))
        return (1, frozenset([node]))
    children = _children(node)
    m = len(children)
    need = math.ceil(_frac(node) * m)
    subs = [_mincost(c, forced, sharedset) for c in children]
    subs.sort(key=lambda x: x[0])
    total = 0
    chosen = set()
    for i in range(need):
        c, s = subs[i]
        total += c
        chosen |= s
    return (total, frozenset(chosen))


def _solve(tree_a, tree_b):
    la = _leaf_set(tree_a)
    lb = _leaf_set(tree_b)
    shared = sorted(la & lb)
    best = None
    for mask in range(1 << len(shared)):
        forced = {shared[i] for i in range(len(shared)) if (mask >> i) & 1}
        c_a, s_a = _mincost(tree_a, forced, shared)
        c_b, s_b = _mincost(tree_b, forced, shared)
        if c_a >= INF or c_b >= INF:
            continue
        merged = s_a | s_b
        k = len(merged)
        if best is None or k < best[0]:
            best = (k, merged)
    if best is None:
        return None
    k, s = best
    return (k, sorted(s))


def _render_tree(node):
    if isinstance(node, str):
        return node
    return "[" + ", ".join([repr(node[0])] + [_render_tree(c) for c in node[1:]]) + "]"


def _parse_answer(answer):
    parts = [p.strip() for p in str(answer).split("|")]
    if len(parts) != 3:
        return None
    try:
        k = int(parts[0])
        a = ast.literal_eval(parts[1])
        b = ast.literal_eval(parts[2])
    except (ValueError, SyntaxError, TypeError):
        return None
    if not isinstance(k, int) or not isinstance(a, list) or not isinstance(b, list):
        return None
    if not a or not all(isinstance(x, str) for x in a) or not all(isinstance(x, str) for x in b):
        return None
    return (k, a, b)


class HierarchicalQuorumOverlap(Task):
    summary = ("Find the smallest cardinality of a common member set that satisfies two nested "
               "threshold organizations; vary branch thresholds, weighted members, and shared "
               "identities; answer the minimum overlap and a witnessing pair")
    design_choice = ("Encode the two organizations as nested lists of member IDs with per-level "
                     "quorum fractions; the solver must output the smallest cardinality of a "
                     "common member set that satisfies both hierarchies, plus one pair of member "
                     "lists achieving it.")
    config_cls = HierarchicalQuorumOverlapConfig

    def generate_entry(self):
        cfg = self.config
        for _ in range(300):
            shared_pool = _SHARED_NAMES[:cfg.shared_pool]
            overlap = random.randint(0, cfg.shared_pool)
            core = random.sample(shared_pool, overlap)
            rest = [s for s in shared_pool if s not in core]
            use_a = core + random.sample(rest, random.randint(0, len(rest)))
            use_b = core + random.sample(rest, random.randint(0, len(rest)))
            priv_a = _PRIVATE_A[:cfg.members]
            priv_b = _PRIVATE_B[:cfg.members]
            tree_a = _build_tree(use_a + priv_a, cfg.depth)
            tree_b = _build_tree(use_b + priv_b, cfg.depth)
            result = _solve(tree_a, tree_b)
            if result is None:
                continue
            k, common = result
            if k < 1:
                continue
            selected = set(common)
            if not (_satisfied(tree_a, selected) and _satisfied(tree_b, selected)):
                continue
            if len(common) != k:
                continue
            break
        else:
            raise RuntimeError("could not generate a valid quorum-overlap instance")

        metadata = edict({
            'tree_a': tree_a,
            'tree_b': tree_b,
            'min_size': int(k),
            'common': list(common),
        })
        ans = f"{k} | {common} | {common}"
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        tree_a = _render_tree(metadata.tree_a)
        tree_b = _render_tree(metadata.tree_b)
        return (
            "Two organizations grant access through layered committees. Each is a nested list: "
            "a committee is a list whose first element is its quorum fraction q (the committee "
            "is approved when at least ceil(q * m) of its m members are approved), and whose "
            "remaining elements are its subcommittees or members; a string is a single person "
            "who is approved exactly when they are selected. The root list is the top "
            "committee, and an organization is approved exactly when its root is approved."
            " Quorum fractions are in (0, 1].\n\n"
            "A person string that appears in both organizations is one and the same person and "
            "may be selected at most once.\n\n"
            f"Org A committee tree: {tree_a}\n"
            f"Org B committee tree: {tree_b}\n\n"
            "Select the fewest distinct people so that BOTH organizations are approved. Apply a "
            "committee DP: the minimum people a committee needs is the sum of the k smallest "
            "needs of its members/subcommittees, where k = ceil(q * m).\n\n"
            "Answer exactly as: <k> | [sorted members] | [sorted members] where the two lists "
            "are identical and equal one witnessing common member set of the minimum size, and "
            "k is that minimum count.\n"
            "Example format: 2 | ['sx', 'a'] | ['sx', 'a']\n"
            "Only the answer line."
        )

    def score_answer(self, answer, entry):
        parsed = _parse_answer(answer)
        if parsed is None:
            return 0.0
        k, a, b = parsed
        if set(a) != set(b):
            return 0.0
        selected = set(a)
        if len(selected) != k:
            return 0.0
        if k != int(entry.metadata.min_size):
            return 0.0
        if not (_satisfied(entry.metadata.tree_a, selected)
                and _satisfied(entry.metadata.tree_b, selected)):
            return 0.0
        return 1.0
