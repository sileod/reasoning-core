import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'terminal_network_coding (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_planning_backtracking_r4/terminal_network_coding',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

PRIMES = [2, 3, 5, 7, 11, 13]


def parse_answer(answer):
    a = answer.strip().lower()
    if a in ("yes", "y", "true", "1"):
        return "yes"
    if a in ("no", "n", "false", "0"):
        return "no"
    return None


def reachable(s, t, adj):
    seen = [False] * len(adj)
    stack = [s]
    seen[s] = True
    while stack:
        v = stack.pop()
        if v == t:
            return True
        for w in adj[v]:
            if not seen[w]:
                seen[w] = True
                stack.append(w)
    return False


@dataclass
class TerminalNetworkCodingV3Config(Config):
    size: int = 3
    erasures: int = 1
    field_char: int = 2

    def apply_difficulty(self, level):
        self.size = 2 + stochastic_rounding(level * 1.2, seed=random.randrange(2**32))
        self.field_char = PRIMES[min(level % len(PRIMES), len(PRIMES) - 1)]
        self.erasures = 1 + stochastic_rounding(level / 2, seed=random.randrange(2**32)) + \
            stochastic_rounding(level / 2, seed=random.randrange(2**32))


class TerminalNetworkCoding(Task):
    summary = ("Choose finite-field mixing coefficients on directed communication networks so "
               "receivers recover specified source symbols despite listed erasure patterns; "
               "return valid local coefficients or impossibility.")
    config_cls = TerminalNetworkCodingV3Config

    def build_layered(self, n_relay_layers, width):
        """Build a layered DAG source -> relays -> sink (complete between consecutive
        layers). Returns nodes (list of names) and edges."""
        nodes = [("S",)]
        layers = []
        for i in range(n_relay_layers):
            layer = [("R", i, j) for j in range(width)]
            layers.append(layer)
            nodes.extend(layer)
        nodes.append(("T",))
        edges = []
        prev = [("S",)]
        for layer in layers:
            for u in prev:
                for v in layer:
                    edges.append((u, v))
            prev = layer
        for u in prev:
            edges.append((u, ("T",)))
        return nodes, edges, [("S",)], [("T",)]

    def layer_boundaries(self, n_relay_layers, width):
        """Return list of boundary index groups: each boundary is a list of edges
        (tuples) that form a cut separating source from sink."""
        boundaries = []
        prev = [("S",)]
        for i in range(n_relay_layers):
            layer = [("R", i, j) for j in range(width)]
            boundaries.append([(u, v) for u in prev for v in layer])
            prev = layer
        boundaries.append([(u, ("T",)) for u in prev])
        return boundaries

    def generate_entry(self):
        size = self.config.size
        fchar = self.config.field_char
        n_erasures = self.config.erasures

        while True:
            n_relay_layers = 1 + random.randrange(0, min(3, 2 + size // 2))
            width = 2 + random.randrange(0, 2 + min(2, size // 2))
            nodes, all_edges, src, dst = self.build_layered(n_relay_layers, width)
            boundaries = self.layer_boundaries(n_relay_layers, width)
            src_name = ("S",)
            dst_name = ("T",)

            feasible = random.random() < 0.5
            erased = set()
            if feasible:
                # erase a moderate set of edges but always keep at least one
                # edge per boundary, so a directed path survives.
                budget = max(0, n_erasures)
                candidates = []
                for b in boundaries:
                    keep = random.choice(b)
                    candidates.extend([e for e in b if e != keep])
                random.shuffle(candidates)
                erased = set(candidates[: min(budget, len(candidates))])
            else:
                # erase one or more full boundaries -> disconnect source from sink
                n_b = len(boundaries)
                picks = random.sample(range(n_b), random.randrange(1, min(3, n_b) + 1))
                erased = set()
                for i in picks:
                    erased |= set(boundaries[i])

            surviving = [e for e in all_edges if e not in erased]
            idx = {name: i for i, name in enumerate(nodes)}
            adj = [[] for _ in nodes]
            for u, v in surviving:
                adj[idx[u]].append(idx[v])
            ok = reachable(idx[src_name], idx[dst_name], adj)
            if ok != feasible:
                # construction invariant violated: reject and resample
                continue
            break

        metadata = {
            "nodes": nodes,
            "edges": [tuple(e) for e in all_edges],
            "source": src_name,
            "sink": dst_name,
            "erasures": [tuple(e) for e in sorted(erased, key=lambda e: (e[0], e[1]))],
            "field_char": fchar,
            "feasible": feasible,
        }
        answer = "yes" if feasible else "no"
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        nodes = metadata["nodes"]
        edges = metadata["edges"]
        src = metadata["source"]
        dst = metadata["sink"]
        field_char = metadata["field_char"]

        node_str = ", ".join(str(n) for n in nodes)
        edge_str = ", ".join(f"{u}->{v}" for u, v in edges)
        erase_str = ", ".join(f"{u}->{v}" for u, v in sorted(metadata["erasures"], key=lambda e: (str(e[0]), str(e[1]))))

        lines = []
        lines.append(
            f"A directed communication network over GF({field_char}) routes a single source "
            f"symbol x (a field element) from source node {src} to receiver node {dst}. "
            f"Relay nodes forward or mix the field elements they receive, so the receiver "
            f"recovers x if and only if at least one directed path from {src} to {dst} "
            f"survives using only working (unerased) edges."
        )
        lines.append(f"Nodes: {node_str}")
        lines.append(f"Edges (u -> v): {edge_str}")
        lines.append(f"The following edges are erased (unavailable): {erase_str}.")
        lines.append(
            f"Can the receiver recover the source symbol x despite these erasures? "
            f"Answer exactly 'yes' or 'no'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        parsed = parse_answer(answer)
        if parsed is None:
            return 0.0
        return 1.0 if parsed == ("yes" if entry.metadata["feasible"] else "no") else 0.0
