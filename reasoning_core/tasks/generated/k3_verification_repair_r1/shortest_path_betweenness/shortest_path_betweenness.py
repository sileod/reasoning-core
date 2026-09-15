"""Shortest-path betweenness centrality: exact single-node betweenness as a rational."""

import random
from dataclasses import dataclass
from fractions import Fraction
from collections import deque

from reasoning_core.template import Config, Entry, Task


def _brandes_betweenness(adj, n, target):
    """Exact betweenness centrality of `target` (unnormalized) via Brandes; Fraction."""
    total = Fraction(0, 1)
    for s in range(n):
        if s == target:
            continue
        dist = [-1] * n
        sigma = [Fraction(0, 1)] * n
        dist[s] = 0
        sigma[s] = Fraction(1, 1)
        order = []
        q = deque([s])
        while q:
            v = q.popleft()
            order.append(v)
            for w in adj[v]:
                if dist[w] == -1:
                    dist[w] = dist[v] + 1
                    q.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
        delta = [Fraction(0, 1)] * n
        for v in reversed(order):
            for w in adj[v]:
                if dist[w] == dist[v] + 1:
                    delta[v] += (sigma[v] / sigma[w]) * (Fraction(1, 1) + delta[w])
            if v == target:
                total += delta[v]
    return total


def _path_counts(adj, n, src):
    """Number of shortest paths from `src` to every vertex; -1 distances for unreachable."""
    dist = [-1] * n
    sigma = [Fraction(0, 1)] * n
    dist[src] = 0
    sigma[src] = Fraction(1, 1)
    q = deque([src])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if dist[w] == -1:
                dist[w] = dist[v] + 1
                q.append(w)
            if dist[w] == dist[v] + 1:
                sigma[w] += sigma[v]
    return dist, sigma


def _brute_betweenness(adj, n, target):
    """Independent check: sum g_st(target)/g_st over ordered (s,t); g_st(v)=sigma_s(v)*sigma_v(t)."""
    from_source = {}
    for s in range(n):
        from_source[s] = _path_counts(adj, n, s)
    precomputed = {}
    total = Fraction(0, 1)
    for s in range(n):
        if s == target:
            continue
        d_s, sigma_s = from_source[s]
        for t in range(n):
            if t == s or t == target or d_s[t] == -1:
                continue
            if t not in precomputed:
                precomputed[t] = _path_counts(adj, n, t)
            d_t, sigma_t = precomputed[t]
            if d_s[t] != d_s[target] + d_t[target]:
                continue
            through = sigma_s[target] * sigma_t[target]
            total += through / sigma_s[t]
    return total


@dataclass
class ShortestPathBetweennessV1Config(Config):
    min_nodes: int = 6
    max_nodes: int = 8
    min_edges: float = 1.1
    max_edges: float = 1.6

    def apply_difficulty(self, level):
        self.min_nodes = 6 + level
        self.max_nodes = 8 + 2 * level


class ShortestPathBetweenness(Task):
    summary = ("From each source, layer an unweighted graph by BFS and count shortest paths, "
               "then accumulate pair dependencies back down the search DAG, returning one node's "
               "exact betweenness as a rational.")
    design_choice = ("Vary the queried node among all vertices, including leaves, centers, and "
                     "articulation points, with graph sizes from 6 to 20 nodes.")
    config_cls = ShortestPathBetweennessV1Config
    task_version = 2

    def generate_entry(self):
        for _ in range(1000):
            n = random.randint(self.config.min_nodes, self.config.max_nodes)
            target = random.randrange(n)
            num_edges = random.randint(n - 1, min(n * (n - 1) // 2, int(n * random.uniform(self.config.min_edges, self.config.max_edges))))
            pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
            random.shuffle(pairs)
            edges = random.sample(pairs, num_edges)
            adj = [set() for _ in range(n)]
            for u, v in edges:
                adj[u].add(v)
                adj[v].add(u)
            # ensure connected
            seen = set()
            q = deque([0])
            seen.add(0)
            while q:
                v = q.popleft()
                for w in adj[v]:
                    if w not in seen:
                        seen.add(w)
                        q.append(w)
            if len(seen) != n:
                continue
            adjacency = [sorted(x) for x in adj]
            gold = _brandes_betweenness(adjacency, n, target)
            check = _brute_betweenness(adjacency, n, target)
            if gold != check:
                raise RuntimeError("betweenness check mismatch")
            answer = f"{gold.numerator}/{gold.denominator}"
            return Entry(metadata={
                "nodes": n,
                "target": target,
                "edges": sorted((min(u, v), max(u, v)) for u, v in edges),
                "adjacency": adjacency,
                "betweenness": answer,
            }, answer=answer)
        raise RuntimeError("failed to generate a connected graph")

    def render_prompt(self, metadata):
        edges = ", ".join(f"{u}-{v}" for u, v in metadata["edges"])
        return (f"Consider the unweighted undirected graph with vertices 0..{metadata['nodes']-1} "
                f"and edges {{ {edges} }}. Compute the exact betweenness centrality of vertex "
                f"{metadata['target']}, defined as the sum over all ordered pairs of vertices "
                f"(s,t) with s,t distinct from {metadata['target']}, of the number of shortest "
                f"s-t paths that pass through {metadata['target']} divided by the total number of "
                f"shortest s-t paths. Give the answer as a single reduced fraction p/q.")

    def score_answer(self, answer, entry):
        try:
            if "/" in str(answer):
                num, den = str(answer).split("/", 1)
                f = Fraction(int(num), int(den))
            else:
                f = Fraction(int(answer), 1)
        except Exception:
            return 0
        num, den = f.numerator, f.denominator
        return 1.0 if f"{num}/{den}" == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'shortest_path_betweenness (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/shortest_path_betweenness',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
