import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _reach(nodes, src, edges, allow):
    adj = {n: [] for n in nodes}
    for (u, v, t) in edges:
        if allow(u, v, t):
            adj[u].append(v)
    seen = set()
    stack = [src]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def _desc(nodes, src, edges):
    return _reach(nodes, src, edges, lambda u, v, t: True)


def has_recanting_witness(nodes, edges, study, out):
    """Recanting-witness criterion (Avin-Shpitser-Pearl): a node W is a witness
    iff it is reachable from `study` by an all-allowed directed path AND by a
    directed b-path (>=1 disallowed edge), and `out` is reachable from W."""
    reach_a = _reach(nodes, study, edges, lambda u, v, t: t == "a")
    reach_all = _desc(nodes, study, edges)
    b_reach = set()
    for (u, v, t) in edges:
        if t == "b" and u in reach_all:
            b_reach |= _reach(nodes, v, edges, lambda a, b2, c: True)
    for w in nodes:
        if w == study:
            continue
        if w in reach_a and w in b_reach and out in _desc(nodes, w, edges):
            return True
    return False


ANS_WITNESS = "recanting_witness"
ANS_IDENT = "identifiable"


@dataclass
class PathIntWorldConfig(Config):
    level: int = 0
    chain_len: int = 3
    n_branches: int = 2
    z_extra: int = 1
    n_alt: int = 1

    def apply_difficulty(self, level):
        self.level = level
        self.chain_len = 3 + (level // 2)
        self.n_branches = 3 + (level // 2)
        self.z_extra = 2 + (level // 3)
        self.n_alt = 1 + (level // 2)


def _build_witness(chain, n_branches, z_extra, n_alt):
    nodes = ["A", "B", "Y"] + chain
    edges = []
    prev = "A"
    for m in chain:
        edges.append((prev, m, "a"))
        prev = m
    edges.append((prev, "Y", "a"))
    edges.append(("A", "B", "b"))
    mj = chain[random.randrange(len(chain))]
    edges.append(("B", mj, "b"))
    for i in range(n_branches):
        anchor = chain[random.randrange(len(chain))]
        bn = f"P{i}"
        nodes.append(bn)
        edges.append((anchor, bn, "a"))
    for i in range(n_alt):
        anchor = chain[random.randrange(len(chain))]
        an = f"F{i}"
        nodes.append(an)
        edges.append((anchor, an, "a"))
        edges.append((an, "Y", "a"))
    for i in range(z_extra):
        bn = f"Q{i}"
        nodes.append(bn)
        edges.append(("B", bn, "b"))
    return nodes, edges


def _build_ident(chain, n_branches, z_extra, n_alt):
    nodes = ["A", "B", "Y"] + chain
    edges = []
    prev = "A"
    for m in chain:
        edges.append((prev, m, "a"))
        prev = m
    edges.append((prev, "Y", "a"))
    edges.append(("A", "B", "b"))
    for i in range(n_branches):
        anchor = chain[random.randrange(len(chain))]
        bn = f"P{i}"
        nodes.append(bn)
        edges.append((anchor, bn, "a"))
    for i in range(n_alt):
        anchor = chain[random.randrange(len(chain))]
        an = f"F{i}"
        nodes.append(an)
        edges.append((anchor, an, "a"))
        edges.append((an, "Y", "a"))
    for i in range(z_extra):
        bn = f"Q{i}"
        nodes.append(bn)
        edges.append(("B", bn, "b"))
    return nodes, edges


class PathInterventionWorldConsistency(Task):
    summary = ("Path-specific-effect identifiability in fully observed causal DAGs with two treatments and "
               "one outcome: trace whether a shared intermediate node on two alternative paths (an allowed "
               "direct path and a disallowed b-path through the second treatment) forms a recanting witness "
               "making the effect non-identifiable; return 'identifiable' or 'recanting_witness'.")
    design_choice = ("Generate instances with two treatment nodes and one outcome, where the witness is the "
                     "shared intermediate node on two alternative paths.")
    config_cls = PathIntWorldConfig

    def generate_entry(self):
        for _ in range(600):
            cfg = self.config
            chain = [f"M{i}" for i in range(cfg.chain_len)]
            if random.random() < 0.5:
                nodes, edges = _build_witness(chain, cfg.n_branches, cfg.z_extra, cfg.n_alt)
                expected = True
            else:
                nodes, edges = _build_ident(chain, cfg.n_branches, cfg.z_extra, cfg.n_alt)
                expected = False
            edges = sorted(edges)
            witness = has_recanting_witness(nodes, edges, "A", "Y")
            if witness != expected:
                continue
            node_order = sorted(nodes)
            answer = ANS_WITNESS if witness else ANS_IDENT
            return Entry(metadata={
                "nodes": node_order,
                "edges": [[u, v, t] for (u, v, t) in edges],
                "study": "A",
                "outcome": "Y",
                "witness": witness,
                "answer": answer,
            }, answer=answer)
        raise RuntimeError("could not generate instance")

    def render_prompt(self, metadata):
        edges = metadata["edges"]
        nodes = ", ".join(metadata["nodes"])
        parts = []
        for (u, v, t) in edges:
            kind = "allowed" if t == "a" else "disallowed"
            parts.append(f"{u}->{v} ({kind})")
        edge_str = "; ".join(parts)
        return (
            f"You are given a fully observed causal DAG over the nodes {{{nodes}}} with no latent "
            f"confounders. We study the path-specific effect of treatment A on the single outcome Y: a "
            f"path-specific causal claim fixes A at the treated level on allowed edges and at the "
            f"counterfactual baseline level on disallowed edges. Edges: {edge_str}.\n"
            "Use the standard recanting-witness criterion of Avin-Shpitser-Pearl: the path-specific "
            "effect is non-identifiable if and only if some intermediate node is reachable from A both "
            "by an all-allowed directed path and by a disallowed b-path, and itself reaches Y -- that "
            "shared intermediate would need two incompatible treatment assignments at once. If any such "
            "recanting witness exists the effect is not identifiable; otherwise it is.\n"
            "Answer exactly one of the two tokens `identifiable` or `recanting_witness`."
        )

    def score_answer(self, answer, entry):
        a = str(answer).strip().lower()
        if a not in (ANS_WITNESS, ANS_IDENT):
            return 0.0
        return 1.0 if a == entry["metadata"]["answer"] else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'path_intervention_world_consistency (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r5/path_intervention_world_consistency',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
