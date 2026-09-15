import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class EulerTourIntervalsConfig(Config):
    n_nodes: int = 8
    n_queries: int = 1

    def apply_difficulty(self, level):
        self.n_nodes = 6 + level * 3
        self.n_queries = 1 + level // 3


def _build_tree(n_nodes):
    if n_nodes <= 1:
        return {0: []}
    children = {i: [] for i in range(n_nodes)}
    for v in range(1, n_nodes):
        parent = random.randrange(v)
        children[parent].append(v)
    return children


def _euler_stamps(children):
    tin = {}
    tout = {}
    timer = 0

    def dfs(u):
        nonlocal timer
        tin[u] = timer
        timer += 1
        for c in children.get(u, []):
            dfs(c)
        tout[u] = timer - 1

    dfs(0)
    return tin, tout


def _parent_list(children, n_nodes):
    parent = [None] * n_nodes
    for par, kids in children.items():
        for kid in kids:
            parent[kid] = par
    return parent


class EulerTourIntervals(Task):
    summary = ("Euler tour interval ancestry queries: over a random rooted tree, compute DFS entry/exit "
               "stamps so each subtree is a contiguous interval, then answer a yes/no 'is u an ancestor "
               "of v' query via stamp inclusion, with balanced yes/no outcome rates across levels.")
    design_choice = ("Answers are yes/no ancestry queries, with trees generated so depth and branching "
                     "make both outcomes equally frequent.")
    config_cls = EulerTourIntervalsConfig
    task_version = 2

    def generate_entry(self):
        config = self.config
        n = config.n_nodes
        children = _build_tree(n)
        tin, tout = _euler_stamps(children)

        is_yes = random.random() < 0.5
        if is_yes:
            for _ in range(64):
                a = random.randrange(n)
                in_subtree = [v for v in range(n) if tin[a] <= tin[v] <= tout[a]]
                if len(in_subtree) >= 2:
                    b = random.choice(in_subtree[1:])
                    break
            else:
                raise RuntimeError("could not build a non-trivial yes query")
            answer = "yes"
        else:
            for _ in range(64):
                a = random.randrange(n)
                outside_a = [v for v in range(n) if not (tin[a] <= tin[v] <= tout[a])]
                if outside_a:
                    b = random.choice(outside_a)
                    break
            else:
                raise RuntimeError("could not build a no query")
            answer = "no"

        metadata = {
            "children": {str(k): sorted(v) for k, v in children.items()},
            "edges": [[p, c] for p, kids in children.items() for c in kids],
            "n_nodes": n,
            "tin": {str(k): v for k, v in tin.items()},
            "tout": {str(k): v for k, v in tout.items()},
            "parent_list": [int(p) if p is not None else None for p in _parent_list(children, n)],
            "query": [a, b],
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        parent_list = metadata["parent_list"]
        parent_str = ", ".join("None" if p is None else str(p) for p in parent_list)
        q = metadata["query"]
        return (
            f"A rooted tree has nodes numbered 0 (the root) through {metadata['n_nodes'] - 1}. "
            f"The parent of each node k is parent[k], where parent[0] is None: [{parent_str}]. "
            "Run a depth-first search from the root and stamp each node u with an entry time tin[u] "
            "and exit time tout[u] such that the subtree rooted at u occupies the contiguous interval "
            f"[tin[u], tout[u]]. Using only these stamps and the subtree-interval property (u is an "
            f"ancestor of v exactly when tin[u] <= tin[v] <= tout[u]), decide: "
            f"is node {q[0]} an ancestor of node {q[1]}? Answer only 'yes' or 'no'."
        )

    def score_answer(self, answer, entry):
        expected = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().lower() == expected.strip().lower() else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'euler_tour_intervals (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/euler_tour_intervals',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
