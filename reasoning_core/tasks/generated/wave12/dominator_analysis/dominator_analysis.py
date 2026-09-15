"""Compute dominator sets and immediate dominators in directed control-flow graphs."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'dominator_analysis (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:dominator_analysis',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/dominator_analysis',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2707068757,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class DominatorConfig(Config):
    node_count: int = 7
    extra_edges: int = 3
    max_nodes: int = 30

    def apply_difficulty(self, level):
        self.node_count = min(self.max_nodes, 6 + 2 * level)
        self.extra_edges = 1 + level


class DominatorAnalysis(Task):
    summary = ("Compute dominator sets and immediate dominators in directed "
               "control-flow graphs from a designated entry node, returning a "
               "queried binary dominator relation (candidate dominates node?).")
    design_choice = ("Query format: return a single binary answer for a given "
                     "pair (node, candidate dominator), with instances "
                     "generated to balance true/false across levels.")
    config_cls = DominatorConfig

    def _dominators(self, graph, entry, node_count):
        dom = {v: set(range(node_count)) for v in range(node_count)}
        dom[entry] = {entry}
        changed = True
        while changed:
            changed = False
            for v in range(node_count):
                if v == entry:
                    continue
                preds = [p for p in range(node_count) if v in graph[p]]
                if not preds:
                    if dom[v] != {v}:
                        dom[v] = {v}
                        changed = True
                    continue
                newd = set(range(node_count))
                for p in preds:
                    newd &= dom[p]
                newd.add(v)
                if newd != dom[v]:
                    dom[v] = newd
                    changed = True
        return dom

    def generate_entry(self):
        n = self.config.node_count
        entry = 0
        while True:
            order = list(range(n))
            random.shuffle(order)
            graph = {v: [] for v in range(n)}
            for i in range(n - 1):
                parent = order[i]
                child = order[i + 1]
                graph[parent].append(child)
            for _ in range(self.config.extra_edges):
                u = random.randrange(n)
                v = random.randrange(n)
                if u != v:
                    graph[u].append(v)
            graph = {v: sorted(set(lst)) for v, lst in graph.items()}
            graph_list = [graph[u] for u in range(n)]
            dom = self._dominators(graph, entry, n)
            if all(len(d) >= 1 for d in dom.values()):
                break

        want_yes = random.random() < 0.5
        for _ in range(64):
            v = random.randrange(n)
            cand = random.randrange(n)
            true_dom = cand in dom[v]
            if true_dom == want_yes:
                answer = "yes" if true_dom else "no"
                return Entry(
                    metadata={
                        "node_count": n,
                        "entry": entry,
                        "graph_list": graph_list,
                        "query_node": v,
                        "candidate": cand,
                        "true_domination": true_dom,
                    },
                    answer=answer,
                )
        v = 0
        cand = 0
        return Entry(
            metadata={
                "node_count": n,
                "entry": entry,
                "graph_list": graph_list,
                "query_node": v,
                "candidate": cand,
                "true_domination": True,
            },
            answer="yes",
        )

    def render_prompt(self, metadata):
        n = metadata["node_count"]
        entry = metadata["entry"]
        graph_list = metadata["graph_list"]
        edges = []
        for u in range(n):
            for w in graph_list[u]:
                edges.append((u, w))
        edge_str = ", ".join(f"({u}->{w})" for u, w in edges)
        v = metadata["query_node"]
        cand = metadata["candidate"]
        return (
            f"Consider the directed control-flow graph on nodes 0..{n - 1} with "
            f"entry node {entry} and edges {edge_str}. "
            f"A node X dominates node Y if every path from the entry to Y passes "
            f"through X (X dominates itself). "
            f"Does node {cand} dominate node {v}? "
            f"Answer exactly 'yes' or 'no'."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip().lower()
        gold = "yes" if entry.metadata["true_domination"] else "no"
        return 1.0 if a == gold else 0.0
