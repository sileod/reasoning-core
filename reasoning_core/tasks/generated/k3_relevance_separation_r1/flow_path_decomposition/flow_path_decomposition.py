import random
from collections import Counter
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class FlowPathConfig(Config):
    num_nodes: int = 4
    num_sources: int = 1
    num_sinks: int = 1
    flow_units: int = 2

    def apply_difficulty(self, level):
        self.num_nodes = 4 + level
        self.num_sources = 1 + level // 2
        self.num_sinks = 1 + level // 2
        self.flow_units = 2 + level


def _decompose(flow, sources, sinks):
    """Canonical greedy path decomposition of an acyclic flow on a DAG.

    Repeatedly start at the smallest source (node in ``sources``) that still
    carries remaining flow, then follow the smallest-labeled outgoing edge with
    positive remaining flow until reaching a sink, then send one unit along the
    resulting path.  Nodes are labeled so every edge goes from a smaller to a
    larger label, which makes every extracted path simple automatically.
    Returns a list of (path, multiplicity) sorted lexicographically by path.
    """
    adjacency = {}
    for (u, v) in flow:
        adjacency.setdefault(u, []).append(v)
    for u in adjacency:
        adjacency[u].sort()
    sources = sorted(sources)
    sinks = set(sinks)
    rem = dict(flow)
    per_path = Counter()
    while rem:
        start = None
        for s in sources:
            if any(rem.get((s, v), 0) > 0 for v in adjacency.get(s, ())):
                start = s
                break
        if start is None:
            raise RuntimeError("flow remains but no source carries it")
        path = [start]
        cur = start
        while cur not in sinks:
            nxt = None
            for v in adjacency.get(cur, ()):
                if rem.get((cur, v), 0) > 0:
                    nxt = v
                    break
            if nxt is None:
                raise RuntimeError("path dead-ends before a sink")
            path.append(nxt)
            cur = nxt
        for a, b in zip(path, path[1:]):
            rem[(a, b)] -= 1
            if rem[(a, b)] == 0:
                del rem[(a, b)]
        per_path[tuple(path)] += 1
    return [(list(p), m) for p, m in sorted(per_path.items())]


def _render(paths):
    return "; ".join(">".join(str(x) for x in p) + ":" + str(m) for p, m in paths)


TASK_META = {'parent_source_id': None,
 'idea': 'flow_path_decomposition (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relevance_separation_r1/flow_path_decomposition',
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
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


class FlowPathDecomposition(Task):
    summary = ("Decompose a feasible acyclic edge flow with integer capacities on a "
               "directed acyclic graph into simple source-sink path flows, cycle flows "
               "excluded, and output the canonically sorted path multiset with integer "
               "flow values.")
    design_choice = ("Represent the input flow as a list of directed edges with integer "
                     "capacities and require decomposition into simple paths between "
                     "specified source-sink pairs, with cycle flows excluded.")
    config_cls = FlowPathConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.num_nodes
        ns, nk = cfg.num_sources, cfg.num_sinks
        if n < ns + nk + 1:
            raise RuntimeError("not enough nodes for source/sink separation")
        sources = list(range(ns))
        sinks = list(range(n - nk, n))

        internals = list(range(ns, n - nk))
        flow = {}
        for _ in range(cfg.flow_units):
            s = random.choice(sources)
            t = random.choice(sinks)
            candidates = [i for i in internals if s < i < t]
            k = random.randint(0, len(candidates))
            interior = sorted(random.sample(candidates, k))
            nodes = [s] + interior + [t]
            for a, b in zip(nodes, nodes[1:]):
                flow[(a, b)] = flow.get((a, b), 0) + 1

        paths = _decompose(flow, sources, sinks)

        check = {}
        for p, mult in paths:
            for a, b in zip(p, p[1:]):
                check[(a, b)] = check.get((a, b), 0) + mult
        if check != flow:
            raise RuntimeError("decomposition does not reproduce the flow")

        capacities = {e: c + random.randint(0, 2) for e, c in flow.items()}

        answer = _render(paths)
        edges = sorted(
            (u, v, capacities[(u, v)], c) for (u, v), c in sorted(flow.items())
        )
        metadata = {
            "sources": sources,
            "sinks": sinks,
            "edges": edges,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        edge_lines = "\n".join(
            f"  {u} -> {v}   (capacity {cap}, flow {f})"
            for u, v, cap, f in metadata["edges"]
        )
        sources = ", ".join(str(x) for x in metadata["sources"])
        sinks = ", ".join(str(x) for x in metadata["sinks"])
        return (
            "We are given a feasible integer edge flow on a directed acyclic graph together "
            "with its edge capacities. Nodes are numbered so that every edge points from a "
            "smaller to a larger number. Sources (net producers) are nodes "
            f"[{sources}] and sinks (net absorbers) are nodes [{sinks}].\n"
            "Edges with their (capacity, flow) values:\n"
            f"{edge_lines}\n"
            "Decompose this flow into simple paths running from a source to a sink using the "
            "canonical greedy: repeatedly start at the smallest source still carrying flow, "
            "then at each node follow the smallest-labeled outgoing edge that still has "
            "remaining flow, stop when a sink is reached, and send one unit along that whole "
            "path. Cycle flows are excluded because the graph is acyclic. Report the resulting "
            "multiset of paths: for each distinct path write 'a>b>...>z:value' with its total "
            "flow value, list the paths sorted lexicographically, and separate them by '; '."
        )
