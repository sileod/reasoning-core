from dataclasses import dataclass
import random

from reasoning_core.template import Task, Entry, Config, edict, render_payload, stochastic_rounding as sround


@dataclass
class TreeReconstructionConfig(Config):
    n_nodes: int = 6

    def apply_difficulty(self, level):
        self.n_nodes = sround(self.n_nodes + 3 * level)


def _random_binary_tree(n):
    """left/right child maps over nodes 0..n-1, rooted at 0: each new node takes a free slot."""
    left, right = {0: None}, {0: None}
    for i in range(1, n):
        slots = [(p, side) for p in range(i) for side, m in (("L", left), ("R", right)) if m[p] is None]
        p, side = random.choice(slots)
        (left if side == "L" else right)[p] = i
        left[i] = right[i] = None
    return left, right


def _walk(i, left, right, order):
    if i is None:
        return []
    kids = _walk(left[i], left, right, order), _walk(right[i], left, right, order)
    return {"pre": [i, *kids[0], *kids[1]], "in": [*kids[0], i, *kids[1]],
            "post": [*kids[0], *kids[1], i]}[order]


QUERIES = ("parent", "left_child", "right_child", "subtree_size", "depth")


class TreeReconstruction(Task):
    summary = "Reconstruct a binary tree from two traversals and answer a structural question about one node."
    config_cls = TreeReconstructionConfig
    task_version = 1

    def generate_entry(self):
        n = max(4, self.config.n_nodes)
        left, right = _random_binary_tree(n)
        labels = random.sample(range(1, 100 if n < 60 else 1000), n)
        parent = {c: p for p in range(n) for c in (left[p], right[p]) if c is not None}
        depth = {0: 0}
        for i in _walk(0, left, right, "pre")[1:]:
            depth[i] = depth[parent[i]] + 1

        qtype = random.choice(QUERIES)
        pool = {"left_child": [i for i in range(n) if left[i] is not None],
                "right_child": [i for i in range(n) if right[i] is not None]}.get(qtype, range(1, n))
        node = random.choice(list(pool))
        answer = {"parent": lambda: labels[parent[node]],
                  "left_child": lambda: labels[left[node]],
                  "right_child": lambda: labels[right[node]],
                  "subtree_size": lambda: len(_walk(node, left, right, "pre")),
                  "depth": lambda: depth[node]}[qtype]()

        pair = random.choice([("pre", "in"), ("in", "post")])
        name = {"pre": "Preorder", "in": "Inorder", "post": "Postorder"}
        payload = {name[o]: [labels[i] for i in _walk(0, left, right, o)] for o in pair}
        ask = {"parent": f"the label of the parent of node {labels[node]}",
               "left_child": f"the label of the left child of node {labels[node]}",
               "right_child": f"the label of the right child of node {labels[node]}",
               "subtree_size": f"the number of nodes in the subtree rooted at node {labels[node]} (including it)",
               "depth": f"the depth of node {labels[node]} (the root has depth 0)"}[qtype]
        metadata = edict(n=n, qtype=qtype, node=labels[node], payload=payload, ask=ask)
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        return (f"A binary tree with distinct node labels has these traversals.\n\n"
                f"{render_payload(metadata.payload)}\n\n"
                f"Reconstruct the tree and report {metadata.ask}. The answer is a single integer.")

    def score_answer(self, answer, entry):
        try:
            return float(int(str(answer).strip()) == int(entry.answer))
        except (TypeError, ValueError):
            return 0.0

    def balancing_key(self, problem):
        return problem.metadata.qtype


TASK_META = {'parent_source_id': None,
 'idea': 'Add binary-tree reconstruction from traversal pairs.',
 'hypothesis': 'N10',
 'changes': 'Implement parent, child, and subtree queries after traversal '
            'reconstruction.',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'adapter_name': 'harness-link',
                'adapter_version': 'harness-link albert 0.3.0',
                'harness_name': 'opencode',
                'harness_version': '1.18.20',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 359706907,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 28,
                             'timeout_seconds': 1200,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
