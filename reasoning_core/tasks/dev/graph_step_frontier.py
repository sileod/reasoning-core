"""graph_successors on general digraphs: the set of nodes reachable in exactly k steps.

graph_successors draws a permutation digraph (out-degree exactly 1), so a query is pointer chasing
along one path. Here out-degree varies from 0 to 3, and the answer is the whole frontier after k
steps (walks, so nodes can repeat), which has to be carried forward one step at a time.
Frontiers that are empty or the whole graph are mostly redrawn.
"""
import random
from dataclasses import dataclass

import networkx as nx

from reasoning_core.tasks.graph_operations import BaseGraphTask
from reasoning_core.template import Config, DevTask, Entry, render_payload, stochastic_rounding as sround


@dataclass
class GraphStepFrontierConfig(Config):
    num_nodes: int = 6
    num_queries: int = 1
    max_hops: int = 2
    max_out_degree: int = 2

    def apply_difficulty(self, level):
        self.num_nodes += level
        self.num_queries = sround(self.num_queries + 0.4 * level)
        self.max_hops += level
        self.max_out_degree = min(3, self.max_out_degree + level // 3)


def frontier(G, x, k):
    nodes = {x}
    for _ in range(k):
        nodes = {v for u in nodes for v in G.successors(u)}
    return sorted(nodes)


class GraphStepFrontier(BaseGraphTask, DevTask):
    summary = "List the nodes reachable in exactly k steps in a directed graph with branching."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or GraphStepFrontierConfig())

    def generate_entry(self):
        c = self.config
        nodes = list(range(c.num_nodes))
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        for u in nodes:
            degree = random.choice([d for d in range(c.max_out_degree + 1) for _ in range(1 if d == 0 else 2)])
            G.add_edges_from((u, v) for v in random.sample(nodes, degree))
        queries, answers = [], []
        while len(queries) < c.num_queries:
            x, k = random.choice(nodes), random.randint(1, c.max_hops)
            f = frontier(G, x, k)
            if (not f or len(f) == len(nodes)) and random.random() < 0.85:
                continue
            queries.append((x, k))
            answers.append(" ".join(map(str, f)) or "none")
        description = self._render_graph(G)
        return Entry(
            {"payload": {"graph": description, "queries": str(queries)}, "queries": queries,
             "edges": sorted(G.edges()), "nodes": nodes},
            " | ".join(answers),
        )

    def render_prompt(self, m):
        return (
            "For each query (x, k), list every node you can be at after following exactly k directed edges "
            "starting from x (a walk may revisit nodes).\n"
            "Answer each query with its nodes in increasing order separated by spaces, or 'none' if no walk "
            "of that length exists; separate queries with ' | ' in query order.\n\n"
            f"{render_payload(m['payload'])}"
        )

    def score_answer(self, answer, entry):
        canon = lambda s: [" ".join(sorted(part.split(), key=lambda t: (not t.isdigit(), int(t) if t.isdigit() else t)))
                           for part in str(s).strip().lower().split("|")]
        pred, true = canon(answer), canon(entry.answer)
        if len(pred) != len(true):
            return 0.0
        return sum(p == t for p, t in zip(pred, true)) / len(true)
