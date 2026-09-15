import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _compute_totals(n, edges):
    """Sum of distances from each node to every other node via two-pass rerooting DP.

    Bottom-up: subtree distance sums. Top-down: reroot along every edge with the
    shift total[child] = total[parent] + n - 2*subtree[child].
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = [-1] * n
    order = []
    stack = [0]
    while stack:
        u = stack.pop()
        order.append(u)
        for w in adj[u]:
            if w == parent[u]:
                continue
            parent[w] = u
            stack.append(w)
    size = [1] * n
    dist_sum = [0] * n
    for u in reversed(order):
        for w in adj[u]:
            if parent[w] == u:
                size[u] += size[w]
                dist_sum[u] += dist_sum[w] + size[w]
    total = [0] * n
    total[0] = dist_sum[0]
    for u in order:
        for w in adj[u]:
            if parent[w] == u:
                total[w] = total[u] + n - 2 * size[w]
    return total


def _independent_total(n, edges, query):
    """Independent check: single-source BFS from the query node, sum all distances."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = [-1] * n
    dist[query] = 0
    frontier = [query]
    while frontier:
        nxt = []
        for u in frontier:
            for w in adj[u]:
                if dist[w] == -1:
                    dist[w] = dist[u] + 1
                    nxt.append(w)
        frontier = nxt
    return sum(d for d in dist if d != -1)


@dataclass
class RerootTreeConfig(Config):
    node_range: tuple = (6, 12)

    def apply_difficulty(self, level):
        self.node_range = (6 + level * 5, 12 + level * 12)


class TreeRerootDistances(Task):
    summary = "Accumulate subtree distance sums on a rooted tree, then reroot along every edge with shift updates, returning a single queried node's total distance to all others."
    design_choice = "Return only the rerooted total distance for a single queried node, with the query node chosen uniformly at random per instance, and the answer is that integer."
    config_cls = RerootTreeConfig

    def generate_entry(self):
        lo, hi = self.config.node_range
        n = random.randint(lo, hi)
        edges = []
        for i in range(1, n):
            p = random.randint(0, i - 1)
            edges.append((p, i))
        total = _compute_totals(n, edges)
        query = random.randint(0, n - 1)
        answer_value = int(total[query])
        assert answer_value == _independent_total(n, edges, query)
        assert isinstance(answer_value, int) and answer_value >= 0
        return Entry(
            metadata={
                "n": n,
                "edges": edges,
                "query": query,
                "answer_value": answer_value,
            },
            answer=str(answer_value),
        )

    def render_prompt(self, metadata):
        edges = "\n".join("  {}-{}".format(u, v) for u, v in metadata["edges"])
        return (
            "A connected, undirected tree on {n} nodes labeled 0..{hi} has edges of "
            "weight 1, so the distance between two nodes is the number of edges on the "
            "path connecting them. The tree is given below as its edges. Use the two-pass "
            "rerooting ('re-rooting') tree DP: a bottom-up pass that accumulates, for each "
            "node, the sum of the distances from it to all nodes in its own subtree, followed "
            "by a top-down pass that reroots across every edge with the shift "
            "(n - 2*subtree_size of the child). Compute the sum of the distances from node "
            "{q} to every other node, and return that total as a single integer.\n"
            "Edges:\n{edges}\n"
            "Query node: {q}\n"
            "Answer: one integer.".format(
                n=metadata["n"], hi=metadata["n"] - 1, q=metadata["query"], edges=edges
            )
        )

    def score_answer(self, answer, entry):
        try:
            gold = int(entry["metadata"]["answer_value"])
        except (KeyError, TypeError, ValueError):
            return 0.0
        try:
            return 1.0 if int(str(answer).strip()) == gold else 0.0
        except (TypeError, ValueError):
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'tree_reroot_distances (draw 2 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/tree_reroot_distances',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1211525277,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
