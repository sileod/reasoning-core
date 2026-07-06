from dataclasses import dataclass
import random

import networkx as nx
import numpy as np

from reasoning_core.template import Config, Problem, Task


SIGNS = {"+": 1, "-": -1}
LABELS = ["increase", "decrease", "no_effect", "ambiguous"]


@dataclass(frozen=True)
class Query:
    kind: str
    source: str
    target: str
    conditioned: frozenset = frozenset()


@dataclass
class Instance:
    graph: nx.DiGraph
    query: Query
    answer: str
    phenomenon: str
    n_extra: int
    p_edge: float


@dataclass
class QualitativeCausalConfig(Config):
    n_extra: int = 8
    p_edge: float = 0.10

    def update(self, c=1):
        self.n_extra += 3 * c
        self.p_edge = min(0.20, self.p_edge + 0.015 * c)

    def apply_difficulty(self, level):
        self.n_extra += 3 * level
        self.p_edge = min(0.20, self.p_edge + 0.015 * level)


def combine_signs(signs):
    signs = set(signs)
    if not signs:
        return "no_effect"
    if signs == {1}:
        return "increase"
    if signs == {-1}:
        return "decrease"
    return "ambiguous"


def edge_sign(G, u, v):
    return G.edges[u, v]["sign"]


def add_edge(G, u, v, sign):
    G.add_edge(u, v, sign=SIGNS[sign])


def intervention_graph(G, x):
    H = G.copy()
    H.remove_edges_from(list(H.in_edges(x)))
    return H


def active_signed_effects(G, source, target, conditioned=frozenset()):
    if source in conditioned or target in conditioned:
        return set()

    H = G.copy()
    for z in conditioned:
        H.remove_edges_from(list(H.in_edges(z)))
        H.remove_edges_from(list(H.out_edges(z)))

    signs = {u: set() for u in H.nodes}
    signs[source].add(1)
    for u in nx.topological_sort(H):
        for v in H.successors(u):
            for sign in signs[u]:
                signs[v].add(sign * edge_sign(H, u, v))
    return signs[target]


def verify_intervention(G, query):
    H = intervention_graph(G, query.source)
    return combine_signs(
        active_signed_effects(H, query.source, query.target, query.conditioned)
    )


def is_collider(G, a, b, c):
    return G.has_edge(a, b) and G.has_edge(c, b)


def undirected_edge_sign(G, u, v):
    if G.has_edge(u, v):
        return edge_sign(G, u, v)
    return edge_sign(G, v, u)


def conditioned_ancestors(G, conditioned):
    out = set(conditioned)
    for z in conditioned:
        out |= nx.ancestors(G, z)
    return out


def active_path_sign(G, path, conditioned=frozenset()):
    opened = conditioned_ancestors(G, conditioned)
    sign = 1

    for u, v in zip(path, path[1:]):
        sign *= undirected_edge_sign(G, u, v)

    for a, b, c in zip(path, path[1:], path[2:]):
        if is_collider(G, a, b, c):
            if b not in opened:
                return None
            sign *= -1
        elif b in conditioned:
            return None

    return sign


def verify_association(G, query):
    if query.source in query.conditioned or query.target in query.conditioned:
        return "no_effect"

    effects = set()
    U = G.to_undirected()
    for path in nx.all_simple_paths(U, query.source, query.target, cutoff=len(G.nodes) - 1):
        sign = active_path_sign(G, path, query.conditioned)
        if sign is not None:
            effects.add(sign)
    return combine_signs(effects)


def verify(G, query):
    if query.kind == "intervention":
        return verify_intervention(G, query)
    if query.kind == "association":
        return verify_association(G, query)
    raise ValueError(query.kind)


def kernel_direct(label, rng):
    G = nx.DiGraph()
    sign = "+" if label == "increase" else "-"
    add_edge(G, "X", "Y", sign)
    return G, Query("intervention", "X", "Y")


def kernel_mediator(label, rng):
    G = nx.DiGraph()
    s1 = rng.choice(["+", "-"])
    s2 = "+" if (label == "increase") == (s1 == "+") else "-"
    add_edge(G, "X", "M", s1)
    add_edge(G, "M", "Y", s2)
    return G, Query("intervention", "X", "Y")


def kernel_blocked_mediator(rng):
    G = nx.DiGraph()
    add_edge(G, "X", "M", "+")
    add_edge(G, "M", "Y", "+")
    return G, Query("intervention", "X", "Y", frozenset({"M"}))


def kernel_competing_paths(rng):
    G = nx.DiGraph()
    add_edge(G, "X", "A", "+")
    add_edge(G, "A", "Y", "+")
    add_edge(G, "X", "B", "+")
    add_edge(G, "B", "Y", "-")
    return G, Query("intervention", "X", "Y")


def kernel_common_cause(label, rng):
    G = nx.DiGraph()
    s1 = rng.choice(["+", "-"])
    s2 = "+" if (label == "increase") == (s1 == "+") else "-"
    add_edge(G, "Z", "X", s1)
    add_edge(G, "Z", "Y", s2)
    return G, Query("association", "X", "Y")


def kernel_closed_collider(rng):
    G = nx.DiGraph()
    add_edge(G, "X", "C", "+")
    add_edge(G, "Y", "C", "+")
    return G, Query("association", "X", "Y")


def kernel_open_collider(rng):
    G = nx.DiGraph()
    add_edge(G, "X", "C", "+")
    add_edge(G, "Y", "C", "+")
    return G, Query("association", "X", "Y", frozenset({"C"}))


def kernel_observe_vs_do_association(rng):
    G = nx.DiGraph()
    add_edge(G, "Z", "X", "+")
    add_edge(G, "Z", "Y", "+")
    return G, Query("association", "X", "Y")


def kernel_observe_vs_do_intervention(rng):
    G = nx.DiGraph()
    add_edge(G, "Z", "X", "+")
    add_edge(G, "Z", "Y", "+")
    return G, Query("intervention", "X", "Y")


def kernel_reverse_path(rng):
    G = nx.DiGraph()
    add_edge(G, "Y", "M", "+")
    add_edge(G, "M", "X", "+")
    return G, Query("intervention", "X", "Y")


def kernel_blocked_negative_mediator(rng):
    G = nx.DiGraph()
    add_edge(G, "X", "M", "-")
    add_edge(G, "M", "Y", "+")
    return G, Query("intervention", "X", "Y", frozenset({"M"}))


KERNELS = {
    "direct_intervention": (["increase", "decrease"], kernel_direct),
    "mediated_intervention": (["increase", "decrease"], kernel_mediator),
    "blocked_mediator": (["no_effect"], lambda label, rng: kernel_blocked_mediator(rng)),
    "competing_paths": (["ambiguous"], lambda label, rng: kernel_competing_paths(rng)),
    "common_cause_association": (["increase", "decrease"], kernel_common_cause),
    "closed_collider": (["no_effect"], lambda label, rng: kernel_closed_collider(rng)),
    "open_collider_explaining_away": (["decrease"], lambda label, rng: kernel_open_collider(rng)),
    "confounded_observation": (["increase"], lambda label, rng: kernel_observe_vs_do_association(rng)),
    "confounded_intervention": (["no_effect"], lambda label, rng: kernel_observe_vs_do_intervention(rng)),
    "reverse_path_no_effect": (["no_effect"], lambda label, rng: kernel_reverse_path(rng)),
    "blocked_negative_mediator": (["no_effect"], lambda label, rng: kernel_blocked_negative_mediator(rng)),
}


def _augmented_topological_order(G, extra, rng):
    order = list(nx.topological_sort(G))
    for node in rng.permutation(extra):
        order.insert(int(rng.integers(len(order) + 1)), node)
    return order


def augment(G, rng, n_extra=8, p_edge=0.12):
    H = G.copy()
    extra = [f"N{i}" for i in range(n_extra)]
    H.add_nodes_from(extra)

    order = _augmented_topological_order(G, extra, rng)
    for i, u in enumerate(order):
        for v in order[i + 1 :]:
            if not H.has_edge(u, v) and rng.random() < p_edge:
                H.add_edge(u, v, sign=int(rng.choice([1, -1])))

    if not nx.is_directed_acyclic_graph(H):
        raise RuntimeError("augment produced cycle")
    return H


def relabel_graph_and_query(G, q, rng):
    names = list(G.nodes)
    shuffled = list(rng.permutation([f"X{i}" for i in range(len(names))]))
    mapping = dict(zip(names, shuffled))
    H = nx.relabel_nodes(G, mapping, copy=True)
    query = Query(
        q.kind,
        mapping[q.source],
        mapping[q.target],
        frozenset(mapping[z] for z in q.conditioned),
    )
    return H, query


def quality_ok(G, q, answer):
    if q.source == q.target:
        return False
    if answer == "no_effect":
        return nx.has_path(G.to_undirected(), q.source, q.target)
    return True


def sample_instance(seed=None, n_extra=8, p_edge=0.10):
    rng = np.random.default_rng(seed)
    phenomena = list(KERNELS)

    for _ in range(1000):
        phenomenon = str(rng.choice(phenomena))
        labels, make = KERNELS[phenomenon]
        target_label = str(rng.choice(labels))

        G, q = make(target_label, rng)
        before = verify(G, q)

        H = augment(G, rng, n_extra=n_extra, p_edge=p_edge)
        ans = verify(H, q)
        if ans != before:
            continue

        H, relabeled_q = relabel_graph_and_query(H, q, rng)
        ans = verify(H, relabeled_q)
        if ans == target_label and quality_ok(H, relabeled_q, ans):
            return Instance(H, relabeled_q, ans, phenomenon, n_extra, p_edge)

    raise RuntimeError("failed to sample valid qualitative causal instance")


def render_edge_list(G):
    lines = []
    for u, v, d in sorted(G.edges(data=True)):
        word = "increase" if d["sign"] == 1 else "decrease"
        lines.append(f"- Increasing {u} tends to {word} {v}.")
    return "\n".join(lines)


def render_compact(G):
    edges = []
    for u, v, d in sorted(G.edges(data=True)):
        word = "increases" if d["sign"] == 1 else "decreases"
        edges.append(f"increasing {u} {word} {v}")
    return "Causal relations: " + "; ".join(edges) + "."


def render_table(G):
    rows = ["cause | effect | sign"]
    for u, v, d in sorted(G.edges(data=True)):
        word = "increase" if d["sign"] == 1 else "decrease"
        rows.append(f"{u} | {v} | {word}")
    return "\n".join(rows)


RENDERERS = [render_edge_list, render_compact, render_table]


class QualitativeCausal(Task):
    def __init__(self, config=QualitativeCausalConfig()):
        super().__init__(config=config)

    def generate(self):
        instance = sample_instance(
            n_extra=self.config.n_extra,
            p_edge=self.config.p_edge,
        )
        edges = [
            (u, v, "+" if d["sign"] == 1 else "-")
            for u, v, d in sorted(instance.graph.edges(data=True))
        ]
        metadata = {
            "edges": edges,
            "nodes": sorted(instance.graph.nodes),
            "query": {
                "kind": instance.query.kind,
                "source": instance.query.source,
                "target": instance.query.target,
                "conditioned": sorted(instance.query.conditioned),
            },
            "query_kind": instance.query.kind,
            "phenomenon": instance.phenomenon,
            "n_extra": instance.n_extra,
            "p_edge": instance.p_edge,
            "association_convention": "opened_colliders_flip_sign",
            "render_style": random.choice(["edge_list", "compact", "table"]),
        }
        return Problem(metadata=metadata, answer=instance.answer)

    def prompt(self, metadata):
        G = nx.DiGraph()
        for u, v, sign in metadata.edges:
            G.add_edge(u, v, sign=SIGNS[sign])
        qd = metadata.query
        q = Query(qd["kind"], qd["source"], qd["target"], frozenset(qd["conditioned"]))
        renderers = {
            "edge_list": render_edge_list,
            "compact": render_compact,
            "table": render_table,
        }
        graph_text = renderers[metadata.render_style](G)

        if q.kind == "intervention":
            cond = ""
            if q.conditioned:
                cond = " while holding " + ", ".join(sorted(q.conditioned)) + " fixed"
            query_text = f"If we intervene to increase {q.source}{cond}, what happens to {q.target}?"
        elif q.kind == "association":
            cond = ""
            if q.conditioned:
                cond = " while conditioning on " + ", ".join(sorted(q.conditioned))
            query_text = f"If we observe {q.source} increasing{cond}, what should we infer about {q.target}?"
        else:
            raise ValueError(q.kind)

        return (
            graph_text
            + f"\n\n{query_text}"
            + "\nAnswer with one of: increase, decrease, no_effect, ambiguous."
        )

    def score_answer(self, answer, entry):
        normalized = str(answer).strip().lower()
        return 1 if normalized == entry.answer else 0

    def balancing_key(self, problem):
        return f"{problem.metadata.phenomenon}:{problem.answer}"
