import random

import networkx as nx

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'd_separation (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:d_separation',
 'changes': 'new task in reasoning_core/tasks/generated/wave12/d_separation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2041304383,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Present the DAG as an adjacency list of directed edges and ask for a yes/no answer on whether two named nodes are d-separated given a set of conditioned nodes."


class dSeparationConfig(Config):
    nodes: int = 7
    edge_prob: float = 0.35
    max_cond: int = 3

    def apply_difficulty(self, level):
        self.nodes = 5 + level
        self.edge_prob = 0.22
        self.max_cond = 1 + level // 2


class d_separation(Task):
    summary = "Determine conditional independence in causal DAGs by active-path reasoning through chains, forks, colliders, and conditioned descendants."
    config_cls = dSeparationConfig

    def generate_entry(self):
        num_nodes = self.config.nodes
        max_cond = min(self.config.max_cond, num_nodes - 2)

        while True:
            edges = []
            for u in range(num_nodes):
                for v in range(u + 1, num_nodes):
                    if random.random() < self.config.edge_prob:
                        edges.append((u, v))
            g = nx.DiGraph()
            g.add_nodes_from(range(num_nodes))
            g.add_edges_from(edges)

            start = random.randrange(num_nodes)
            end = random.choice([n for n in range(num_nodes) if n != start])

            others = [n for n in range(num_nodes) if n not in (start, end)]
            random.shuffle(others)
            k_cond = random.randrange(0, max_cond + 1)
            conditioned = others[:k_cond]

            sep = nx.is_d_separator(g, {start}, {end}, set(conditioned))

            return Entry(
                metadata={
                    "nodes": num_nodes,
                    "edges": sorted(edges),
                    "start": start,
                    "end": end,
                    "conditioned": sorted(conditioned),
                    "separated": sep,
                },
                answer="yes" if sep else "no",
            )

    def render_prompt(self, metadata):
        edges = ", ".join(f"{u}->{v}" for u, v in metadata["edges"])
        cond = ", ".join(str(c) for c in metadata["conditioned"])
        if not cond:
            cond = "none"
        return (
            f"Consider the following causal DAG (nodes are integers) with directed edges "
            f"{edges}. Are nodes {metadata['start']} and {metadata['end']} d-separated "
            f"given the conditioning set {{{cond}}}? "
            "Answer exactly 'yes' or 'no'."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = entry.answer
        a = answer.strip().lower()
        return 1.0 if a == gold else 0.0
