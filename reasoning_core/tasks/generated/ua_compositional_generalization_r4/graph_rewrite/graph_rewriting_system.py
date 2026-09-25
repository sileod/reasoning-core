import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _fmt_graph(nodes, edges):
    ns = ",".join(str(n) for n in sorted(nodes))
    es = ",".join(f"({a},{b})" for a, b in sorted(tuple(sorted(e)) for e in edges))
    return f"{ns}|{es}"


def _iso_maps(lv, le, gv, ge):
    gv = sorted(gv)
    lvl = sorted(lv)
    if len(lvl) > len(gv):
        return []
    maps = []
    for perm in itertools.permutations(gv, len(lvl)):
        m = dict(zip(lvl, perm))
        if all((min(m[a], m[b]), max(m[a], m[b])) in ge for a, b in le):
            maps.append(m)
    return maps


def _nac_blocked(m, nac_nv, nac_ne, lhs_nodes, gv, ge):
    used = set(m.values())
    avail = [x for x in sorted(gv) if x not in used]
    extra = [n for n in sorted(nac_nv) if n not in lhs_nodes]
    if len(extra) > len(avail):
        return False
    for perm in itertools.permutations(avail, len(extra)):
        psi = dict(m)
        for en, g in zip(extra, perm):
            psi[en] = g
        if all((min(psi[a], psi[b]), max(psi[a], psi[b])) in ge for a, b in nac_ne):
            return True
    return False


def _rule_matches(G, rule):
    V, E = G
    res = []
    for m in _iso_maps(rule["lv"], rule["le"], V, E):
        if any(_nac_blocked(m, nv, ne, rule["lv"], V, E) for nv, ne in rule["nacs"]):
            continue
        res.append(tuple(m[x] for x in sorted(rule["lv"])))
    return res


def _fresh_ids(V, k):
    used = set(V)
    out = []
    x = 0
    while len(out) < k:
        if x not in used:
            out.append(x)
        x += 1
    return out


def _apply(G, rule, match):
    V, E = G
    m = dict(zip(sorted(rule["lv"]), match))
    fresh = _fresh_ids(V, len(rule["rv"]))
    rmap = dict(zip(sorted(rule["rv"]), fresh))
    img = set(m.values())
    nV = (V - img) | set(fresh)
    nE = set((a, b) for (a, b) in E if a not in img and b not in img)
    for a, b in rule["re"]:
        nE.add((min(rmap[a], rmap[b]), max(rmap[a], rmap[b])))
    return nV, nE


def _smallest_match(G, rule):
    ms = _rule_matches(G, rule)
    if not ms:
        return None
    return min(ms)


def _exhaust(G, rule):
    seq = [G]
    napp = 0
    while True:
        match = _smallest_match(G, rule)
        if match is None:
            break
        G = _apply(G, rule, match)
        seq.append(G)
        napp += 1
    return seq, napp


def _rand_edges(n, p, min_edges=0):
    es = set()
    for a in range(n):
        for b in range(a + 1, n):
            if random.random() < p:
                es.add((a, b))
    guard = 0
    while len(es) < min_edges and guard < 200:
        a, b = random.randrange(n), random.randrange(n)
        if a != b:
            es.add((min(a, b), max(a, b)))
        guard += 1
    return es


def _contains(tv, te, gv, ge):
    if len(tv) > len(gv):
        return False
    return len(_iso_maps(tv, te, gv, ge)) > 0


@dataclass
class GraphRewriteV2Config(Config):
    max_nodes: int = 4
    max_lhs: int = 2
    max_steps: int = 2
    max_edges: int = 4
    nac_prob: float = 0.3

    def apply_difficulty(self, level):
        self.max_nodes = 4 + level
        self.max_lhs = 2 + (level >= 3) + (level >= 5)
        self.max_steps = 2 + level
        self.max_edges = 4 + 2 * level
        self.nac_prob = 0.3 + 0.1 * level


class GraphRewriteV2(Task):
    task_name = "graph_rewrite"
    summary = ("Apply graph rewriting rules with node matching and replacement, including "
               "dangling edges and negative application conditions; modes ask for the final "
               "graph, the number of rule applications, or whether a target subgraph appears.")
    design_choice = ("Use string-encoded graphs where nodes are integers and edges are pairs; "
                     "answers are strings like 'G1->G2' for rule sequences.")
    config_cls = GraphRewriteV2Config
    task_version = 2

    def _build_rule(self, cfg):
        lhs_size = random.randint(2, cfg.max_lhs)
        rhs_size = random.randint(1, lhs_size - 1)
        lv = frozenset(range(lhs_size))
        rv = frozenset(range(rhs_size))
        p = 0.5
        le = frozenset(_rand_edges(lhs_size, p, min_edges=0))
        re = frozenset(_rand_edges(rhs_size, p, min_edges=0))
        nacs = []
        if random.random() < cfg.nac_prob and lhs_size + 1 <= cfg.max_nodes:
            extra = random.randint(1, 2)
            nsz = lhs_size + extra
            nv = frozenset(range(nsz))
            ne = set(_rand_edges(nsz, p, min_edges=0))
            ne |= set(le)
            for x in range(lhs_size):
                y = random.randrange(lhs_size, nsz)
                ne.add((min(x, y), max(x, y)))
            nacs.append((nv, frozenset(ne)))
        return {"lv": lv, "rv": rv, "le": le, "re": re, "nacs": nacs}

    def _start_graph(self, cfg, rule):
        lhs_size = len(rule["lv"])
        n = random.randint(max(lhs_size, 2), cfg.max_nodes)
        edges = _rand_edges(n, 0.35, min_edges=0)
        for a, b in rule["le"]:
            edges.add((a, b))
        return set(range(n)), edges

    def _target(self, G, present):
        V, E = G
        gvl = sorted(V)
        if not E:
            return None
        for _ in range(300):
            t = random.randint(2, 3)
            if t > len(V):
                continue
            subs = random.sample(gvl, t)
            te = set((a, b) for a in subs for b in subs if a < b and (a, b) in E)
            if not te:
                continue
            if present:
                return set(subs), te
            if not _contains(set(subs), te, V, E):
                return set(subs), te
        absent = [(a, b) for a, b in itertools.combinations(gvl, 2) if (a, b) not in E]
        if absent:
            return set(absent[0]), set([absent[0]])
        e = random.choice(tuple(sorted(E)))
        return set(e), set([e])

    def generate_entry(self):
        cfg = self.config
        mode = random.choice(["derive", "count", "appears"])
        G = None
        rule = self._build_rule(cfg)
        G = self._start_graph(cfg, rule)
        seq, napp = _exhaust(G, rule)
        Gf = seq[-1]

        if mode == "derive":
            answer = "->".join(_fmt_graph(v, e) for v, e in seq)
            meta = {
                "mode": "derive",
                "rule": {
                    "lhs": _fmt_graph(rule["lv"], rule["le"]),
                    "rhs": _fmt_graph(rule["rv"], rule["re"]),
                    "nac": ", ".join(_fmt_graph(nv, ne) for nv, ne in rule["nacs"]),
                },
                "start": _fmt_graph(*G),
                "answer_sequence": answer,
            }
        elif mode == "count":
            answer = str(napp)
            meta = {
                "mode": "count",
                "rule": {
                    "lhs": _fmt_graph(rule["lv"], rule["le"]),
                    "rhs": _fmt_graph(rule["rv"], rule["re"]),
                    "nac": ", ".join(_fmt_graph(nv, ne) for nv, ne in rule["nacs"]),
                },
                "start": _fmt_graph(*G),
                "applications": napp,
            }
        else:
            target = None
            present = None
            for _ in range(50):
                if not Gf[1]:
                    rule = self._build_rule(cfg)
                    G = self._start_graph(cfg, rule)
                    seq, napp = _exhaust(G, rule)
                    Gf = seq[-1]
                    continue
                present = random.random() < 0.5
                target = self._target(Gf, present)
                if target is not None:
                    break
            if target is None:
                return self.generate_entry()
            tv, te = target
            meta = {
                "mode": "appears",
                "rule": {
                    "lhs": _fmt_graph(rule["lv"], rule["le"]),
                    "rhs": _fmt_graph(rule["rv"], rule["re"]),
                    "nac": ", ".join(_fmt_graph(nv, ne) for nv, ne in rule["nacs"]),
                },
                "start": _fmt_graph(*G),
                "target": _fmt_graph(tv, te),
            }
            answer = "Yes" if present else "No"
        return Entry(metadata=meta, answer=answer)

    def render_prompt(self, metadata):
        rule = metadata["rule"]
        lines = [
            "You are working with a graph rewriting system. A graph is written as <nodes>|<edges>, "
            "where <nodes> is a comma-separated list of node labels and <edges> a comma-separated "
            "list of unordered edges. For example the graph with nodes 0,1,2 and edges (0,1),(1,2) "
            "is written  0,1,2|(0,1),(1,2) , and a graph with two nodes and no edges is written  0,1| .",
            "",
            "A rewrite rule  A => B  replaces an occurrence of subgraph A with subgraph B. When the "
            "rule is applied, the matched nodes of A are deleted together with every edge incident to "
            "them (any dangling edge), and the nodes of B are added with fresh labels together with "
            "their listed edges.",
        ]
        rule_txt = f"  {rule['lhs']}  =>  {rule['rhs']}"
        if rule["nac"]:
            rule_txt += f"   (blocked whenever a copy of {rule['nac']} also extends the match)"
        lines += [
            "",
            "The rule is:",
            rule_txt,
            "",
            "When applying the rule repeatedly, always pick the lexicographically smallest match: "
            "list the images of the left-side nodes in order of their labels and choose the "
            "lexicographically smallest such tuple.",
            "",
            f"Start graph: {metadata['start']}",
        ]
        mode = metadata["mode"]
        if mode == "derive":
            lines += [
                "",
                "Starting from the start graph, repeatedly apply the rule at the lexicographically "
                "smallest match until the rule can no longer be applied. Give the full sequence of "
                "graphs reached, including the start graph and the graph after every single "
                "application, joined with '->'. For example a valid answer format is  0,1,2|(0,1),"
                "(1,2)->0,1,2|(1,2) .",
            ]
        elif mode == "count":
            lines += [
                "",
                "Starting from the start graph, repeatedly apply the rule at the lexicographically "
                "smallest match until the rule can no longer be applied. What is the total number of "
                "applications? Answer with a single integer.",
            ]
        else:
            lines += [
                "",
                f"Target subgraph: {metadata['target']}",
                "",
                "Starting from the start graph, repeatedly apply the rule at the lexicographically "
                "smallest match until the rule can no longer be applied. In the resulting graph, is "
                "the target subgraph present? Answer Yes or No.",
            ]
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'graph_rewriting_system (variant 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r4/graph_rewriting_system',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3020341981,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
