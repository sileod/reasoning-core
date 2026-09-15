"""Chained axis-step navigation over ordered labeled trees.

Each example emits one ordered rooted tree in parenthesized notation, a stated
context node, and a chain of axis steps (child, parent, descendant, ancestor,
following-sibling, preceding-sibling) each with a 1-based positional filter in
document order. The solver tracks every distinct context node visited (the
starting node plus each step's result) and reports their ids sorted ascending.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

AXES = [
    "child",
    "parent",
    "descendant",
    "ancestor",
    "following-sibling",
    "preceding-sibling",
]


def _build_tree(size):
    children = {i: [] for i in range(size)}
    parent = {0: None}
    for i in range(1, size):
        p = random.randrange(i)
        parent[i] = p
        children[p].append(i)
    for kids in children.values():
        random.shuffle(kids)
    order = []
    stack = [0]
    while stack:
        x = stack.pop()
        order.append(x)
        stack.extend(reversed(children[x]))
    rank = {x: i for i, x in enumerate(order)}
    return children, parent, rank


def _axis(node, axis, children, parent):
    if axis == "child":
        return list(children[node])
    if axis == "parent":
        p = parent[node]
        return [] if p is None else [p]
    if axis == "following-sibling":
        p = parent[node]
        if p is None:
            return []
        kids = children[p]
        return kids[kids.index(node) + 1:]
    if axis == "preceding-sibling":
        p = parent[node]
        if p is None:
            return []
        kids = children[p]
        return kids[: kids.index(node)]
    if axis == "descendant":
        res = []

        def walk(x):
            for c in children[x]:
                res.append(c)
                walk(c)

        walk(node)
        return res
    if axis == "ancestor":
        res = []
        x = parent[node]
        while x is not None:
            res.append(x)
            x = parent[x]
        res.reverse()
        return res
    raise ValueError(axis)


def _render_tree(node, children):
    body = str(node)
    kids = children[node]
    if kids:
        body += "(" + ",".join(_render_tree(c, children) for c in kids) + ")"
    return body


def _parse_list(text):
    s = str(text).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    parts = [p.strip() for p in s.split(",") if p.strip() != ""]
    return [int(p) for p in parts]


@dataclass
class TreeAxisConfig(Config):
    size: int = 6
    n_steps: int = 2

    def apply_difficulty(self, level):
        self.size = 6 + 2 * level
        self.n_steps = 2 + level // 2


class TreeAxisNavigation(Task):
    summary = (
        "Evaluate chained axis steps (child, parent, descendant, ancestor, "
        "following- and preceding-sibling, with positional filters) from a stated "
        "context node over ordered labeled trees, returning the sorted ids of all "
        "reached nodes."
    )
    config_cls = TreeAxisConfig
    task_version = 3

    def generate_entry(self):
        size = self.config.size
        children, parent, rank = _build_tree(size)
        context = random.randrange(size)
        steps = []
        visited = [context]
        node = context
        for _ in range(self.config.n_steps):
            nonempty = {}
            for axis in AXES:
                cands = sorted(_axis(node, axis, children, parent), key=rank.get)
                if cands:
                    nonempty[axis] = cands
            multi = [a for a, v in nonempty.items() if len(v) >= 2]
            if multi and random.random() < 0.6:
                axis = random.choice(sorted(multi))
            else:
                axis = random.choice(sorted(nonempty))
            arr = nonempty[axis]
            k = random.randrange(1, len(arr) + 1)
            node = arr[k - 1]
            steps.append((axis, k))
            visited.append(node)
        reached = sorted(set(visited))
        for x in reached:
            assert isinstance(x, int)
        answer = "[" + ", ".join(str(x) for x in reached) + "]"
        metadata = {
            "size": size,
            "tree": _render_tree(0, children),
            "children": {str(k): list(v) for k, v in children.items()},
            "context": context,
            "steps": [(a, k) for a, k in steps],
            "visited": visited,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        steps = "\n".join(
            f"{i}. {axis}[{k}]" for i, (axis, k) in enumerate(metadata["steps"], 1)
        )
        return (
            "Use the ordered rooted tree below, written in parenthesized notation "
            "where a node lists its children left-to-right and a group with no "
            "children is a leaf.\n\n"
            f"Tree: {metadata['tree']}\n"
            f"Context node: {metadata['context']}\n\n"
            "Apply each axis step below in order; each step's result becomes the "
            "context for the next. The axes child, parent, descendant, ancestor, "
            "following-sibling and preceding-sibling act on the current context "
            "node, and the bracketed 1-based number selects that element of the "
            "axis result in document order (preorder, left to right).\n\n"
            f"Steps:\n{steps}\n\n"
            "Report the ids of every distinct node visited as a context, including "
            "the starting node, sorted ascending as a comma-separated list inside "
            "square brackets, e.g. [2, 5, 9]."
        )

    def score_answer(self, answer, entry):
        try:
            got = _parse_list(answer)
            gold = _parse_list(entry["answer"])
        except (ValueError, TypeError):
            return 0.0
        return 1.0 if got == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'tree_axis_navigation (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_transfer_r1/tree_axis_navigation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
