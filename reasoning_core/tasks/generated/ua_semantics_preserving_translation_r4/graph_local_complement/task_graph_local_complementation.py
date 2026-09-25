import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _local_complement(adj, v):
    n = len(adj)
    nbrs = [i for i in range(n) if adj[v][i]]
    for idx, a in enumerate(nbrs):
        for b in nbrs[idx + 1:]:
            adj[a][b] = not adj[a][b]
            adj[b][a] = not adj[b][a]


def _edge_pivot(adj, u, v):
    n = len(adj)
    for w in range(n):
        if w == v or not adj[u][w]:
            continue
        for x in range(n):
            if x == u or not adj[v][x]:
                continue
            adj[w][x] = not adj[w][x]
            adj[x][w] = not adj[x][w]
    _local_complement(adj, u)
    _local_complement(adj, v)


def _delete(alive, adj, v):
    alive.remove(v)
    for i in range(len(adj)):
        adj[v][i] = False
        adj[i][v] = False
    for i in range(len(adj)):
        adj[i][i] = False


@dataclass
class GCGConfig(Config):
    level: int = 0
    n: int = 5
    seed: int = 0

    def apply_difficulty(self, level):
        self.level = level
        self.n = int(4 + level)


class GraphLocalComplementV1(Task):
    task_name = "graph_local_complement"
    summary = "Apply sequences of neighborhood complementation, edge pivots, and vertex deletion to labeled simple graphs; track changing neighborhoods per operation and return whether a queried surviving edge is present (yes/no)."
    config_cls = GCGConfig
    design_choice = "Use vertex deletion to remove high-degree hubs, forcing solvers to recompute neighborhoods after each local complementation rather than relying on global structure."  # copied verbatim

    def generate_entry(self):
        while True:
            n = int(self.config.n)
            ops = int(3 + self.config.level)
            adj = [[False] * n for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    if random.random() < 0.5:
                        adj[i][j] = True
                        adj[j][i] = True
            init_edges = sorted(
                (min(a, b), max(a, b))
                for a in range(n) for b in range(a + 1, n) if adj[a][b]
            )
            if not init_edges:
                continue
            random.shuffle(init_edges)
            alive = list(range(n))
            sequence = []
            for _ in range(ops):
                if not alive:
                    break
                op = random.choice(['lc', 'pivot', 'del'])
                if op == 'lc':
                    v = random.choice(alive)
                    _local_complement(adj, v)
                    sequence.append(('lc', v))
                elif op == 'pivot':
                    candidates = [x for x in alive if any(adj[x][y] for y in alive)]
                    if not candidates:
                        break
                    u = random.choice(candidates)
                    rest = [x for x in alive if x != u and adj[u][x]]
                    if not rest:
                        break
                    v = random.choice(rest)
                    _edge_pivot(adj, u, v)
                    sequence.append(('pivot', u, v))
                else:
                    if len(alive) <= 1:
                        break
                    v = random.choice(alive)
                    _delete(alive, adj, v)
                    sequence.append(('del', v))
            alive_set = set(alive)
            pairs = [
                (a, b) for a in range(n) for b in range(a + 1, n)
                if a in alive_set and b in alive_set
            ]
            if not pairs:
                continue
            tgt = random.random() < 0.5
            present = [p for p in pairs if adj[p[0]][p[1]]]
            absent = [p for p in pairs if not adj[p[0]][p[1]]]
            if tgt and present:
                u, v = present[0] if len(present) == 1 else random.choice(present)
                ans = "yes"
            elif not tgt and absent:
                u, v = absent[0] if len(absent) == 1 else random.choice(absent)
                ans = "no"
            else:
                continue
            metadata = {
                "n": n,
                "init_edges": init_edges,
                "sequence": sequence,
                "query": [u, v],
            }
            return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        n = metadata["n"]
        lines = [f"Starting edge list:"]
        lines.append(" ".join(f"({a},{b})" for a, b in metadata["init_edges"]))
        lines.append(f"This is a simple undirected graph on vertices 0..{n - 1}.")
        lines.append("")
        lines.append("Apply in order:")
        for op in metadata["sequence"]:
            if op[0] == "lc":
                lines.append(f"local complement at vertex {op[1]}")
            elif op[0] == "pivot":
                lines.append(f"pivot on edge ({op[1]},{op[2]})")
            else:
                lines.append(f"delete vertex {op[1]}")
        lines.append("")
        q = metadata["query"]
        lines.append(
            f"Reply yes if the queried edge is present after all operations, and no otherwise."
        )
        lines.append(f"Is the edge ({q[0]},{q[1]}) present?")
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'graph_local_complementation (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_semantics_preserving_translation_r4/graph_local_complementation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
