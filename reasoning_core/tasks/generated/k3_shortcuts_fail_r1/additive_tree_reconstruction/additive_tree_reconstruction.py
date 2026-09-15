import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround

TASK_META = {'parent_source_id': None,
 'idea': 'additive_tree_reconstruction (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/additive_tree_reconstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


@dataclass
class AdditiveTreeConfig(Config):
    n_leaves: int = 4
    max_weight: int = 6
    max_attempts: int = 60

    def apply_difficulty(self, level):
        self.n_leaves = min(4 + 2 * level, 16)
        self.max_weight = 6 + 3 * level


def _build_tree(n_leaves, max_weight):
    adj = {i: [] for i in range(n_leaves)}
    root = n_leaves
    adj[root] = []
    for lf in range(3):
        w = random.randint(1, max_weight)
        adj[lf].append((root, Fraction(w)))
        adj[root].append((lf, Fraction(w)))
    next_internal = n_leaves + 1
    for leaf in range(3, n_leaves):
        possible = [(u, v) for u in adj for v, _ in adj[u] if u < v]
        a, b = random.choice(possible)
        w = _edge_weight(adj, a, b)
        v = next_internal
        next_internal += 1
        adj[v] = []
        _remove_edge(adj, a, b)
        wleaf = random.randint(1, max_weight)
        w1 = random.randint(1, max(1, int(w) - 1))
        adj[a].append((v, Fraction(w1))); adj[v].append((a, Fraction(w1)))
        adj[b].append((v, Fraction(w - w1))); adj[v].append((b, Fraction(w - w1)))
        adj[leaf].append((v, Fraction(wleaf))); adj[v].append((leaf, Fraction(wleaf)))
    return adj


def _edge_weight(adj, a, b):
    for v, w in adj[a]:
        if v == b:
            return w
    raise RuntimeError("edge missing")


def _remove_edge(adj, a, b):
    adj[a] = [x for x in adj[a] if x[0] != b]
    adj[b] = [x for x in adj[b] if x[0] != a]


def _bfs_path(adj, start, goal):
    prev = {start: None}
    stack = [start]
    while stack:
        u = stack.pop()
        if u == goal:
            break
        for v, _ in adj[u]:
            if v not in prev:
                prev[v] = u
                stack.append(v)
    if goal not in prev:
        raise RuntimeError("no path")
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    return path


def _leaf_dist_matrix(adj, leaves):
    n = len(leaves)
    D = {}
    order = dict((l, i) for i, l in enumerate(leaves))
    for a in leaves:
        D[order[a]] = {}
        for b in leaves:
            if b == a:
                D[order[a]][order[b]] = Fraction(0)
                continue
            path = _bfs_path(adj, a, b)
            s = Fraction(0)
            for e in range(len(path) - 1):
                s += _edge_weight(adj, path[e], path[e + 1])
            D[order[a]][order[b]] = s
    return D, order


def _is_binary(adj, n_leaves):
    for u in range(n_leaves):
        if len(adj[u]) != 1:
            return False
    internals = [u for u in adj if u >= n_leaves]
    if len(internals) != n_leaves - 2:
        return False
    for u in internals:
        if len(adj[u]) != 3:
            return False
    return all(w > 0 for u in adj for v, w in adj[u])


def _verify_answer(edges, dist, n_leaves):
    adj = {}
    for p, c, w in edges:
        adj.setdefault(p, []).append((c, w))
        adj.setdefault(c, []).append((p, w))
    try:
        D2, order = _leaf_dist_matrix(adj, list(range(n_leaves)))
    except RuntimeError:
        return False
    for a in range(n_leaves):
        for b in range(n_leaves):
            if D2[order[a]][order[b]] != dist[a][b]:
                return False
    return True


def _canonical_answer(adj, n_leaves):
    rooted = _root_at(adj, 0)
    edges = []
    for parent in sorted(rooted):
        for child in sorted(rooted[parent]):
            edges.append((parent, child, _edge_weight(adj, parent, child)))
    edges.sort()
    return edges


def _root_at(adj, root):
    rooted = {}
    stack = [(root, None)]
    while stack:
        u, par = stack.pop()
        rooted.setdefault(u, [])
        for v, _ in adj[u]:
            if v == par:
                continue
            rooted[u].append(v)
            stack.append((v, u))
    return rooted


def _format_answer(edges):
    return " ".join(f"{p}-{c}:{w}" for p, c, w in edges)


def _parse_answer(s):
    if not isinstance(s, str):
        return None
    tokens = s.split()
    edges = []
    try:
        for t in tokens:
            pcs = t.split(":")
            if len(pcs) != 2:
                return None
            w = Fraction(pcs[1])
            pp = pcs[0].split("-")
            if len(pp) != 2:
                return None
            edges.append((int(pp[0]), int(pp[1]), w))
    except Exception:
        return None
    return edges


class AdditiveTreeReconstruction(Task):
    summary = ("Reconstruct the unique edge-weighted tree realizing an additive leaf-distance "
               "matrix: detect cherries by the four-point criterion, peel leaves, shorten "
               "pendant edges, recurse; answer is the canonical weighted edge list.")
    design_choice = ("Choose leaf labels as integers 0..n-1 in insertion order, and emit edges "
                     "sorted by parent then child, with weights as irreducible fractions.")
    config_cls = AdditiveTreeConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_leaves
        for _ in range(cfg.max_attempts):
            adj = _build_tree(n, cfg.max_weight)
            leaves = list(range(n))
            D_num, _order = _leaf_dist_matrix(adj, leaves)
            if not _is_binary(adj, n):
                continue
            edges = _canonical_answer(adj, n)
            if not _verify_answer(edges, D_num, n):
                continue
            answer = _format_answer(edges)
            dist_rows = [["0" if i == j else str(D_num[i][j]) for j in range(n)] for i in range(n)]
            metadata = edict(
                n_leaves=n,
                max_weight=cfg.max_weight,
                dist=dist_rows,
                leaves=leaves,
                payload=_payload(D_num, n),
            )
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("Failed to generate a valid additive tree instance")

    def render_prompt(self, metadata):
        rows = []
        n = metadata.n_leaves
        dist = metadata.dist
        for i in range(n):
            vals = " ".join(dist[i][j] for j in range(i + 1, n))
            rows.append(f"  {i}: {vals}")
        matrix = "\n".join(rows)
        return (
            "The leaves of an unknown edge-weighted tree are labelled 0 through "
            f"{n - 1}. Every internal node has degree 3, every edge has a positive "
            "length, and the distance between two leaves equals the sum of the "
            "lengths of the edges on the unique path between them. Below is the "
            "additive distance matrix: row i lists the distances from leaf i to "
            f"leaves i+1 ... {n - 1} (in order).\n"
            f"{matrix}\n"
            "Reconstruct the unique edge-weighted tree realizing this matrix (the "
            "additive phylogeny reconstruction). Emit every edge as "
            "'parent-child:weight', with the tree rooted at leaf 0, edges sorted by "
            "parent then child, and each weight an irreducible fraction. The answer "
            f"is {2 * n - 3} space-separated edges."
        )

    def score_answer(self, answer, entry):
        got = _parse_answer(answer)
        want = _parse_answer(entry.answer)
        if got is None or want is None:
            return 0.0
        return 1.0 if got == want else 0.0


def _payload(dist, n):
    out = []
    for i in range(n):
        out.append([str(dist[i][j]) for j in range(i + 1, n)])
    return out
