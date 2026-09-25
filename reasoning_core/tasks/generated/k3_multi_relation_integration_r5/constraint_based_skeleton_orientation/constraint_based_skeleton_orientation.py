import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _run_pc(n, ci_triples):
    """PC skeleton search + v-structure orientation + Meek completion.

    Returns sorted list of directed edges (u, v) meaning u -> v.
    """
    nodes = list(range(n))
    adj = {x: set(nodes) - {x} for x in nodes}
    sep_map = {}
    for (a, b, sep) in ci_triples:
        a, b = sorted((a, b))
        if b in adj[a]:
            adj[a].discard(b)
            adj[b].discard(a)
        sep_map[(a, b)] = set(sep)

    adj_x = {x: set(adj[x]) for x in nodes}
    directed = set()

    for (a, b, sep) in ci_triples:
        a, b = sorted((a, b))
        sep = sep_map[(a, b)]
        for c in nodes:
            if c == a or c == b:
                continue
            if c in adj_x[a] and c in adj_x[b] and c not in sep:
                directed.add((a, c))
                directed.add((b, c))

    changed = True
    while changed:
        changed = False

        R1 = []
        for x in nodes:
            for y in nodes:
                if (x, y) not in directed:
                    continue
                for w in nodes:
                    if w == x or w == y:
                        continue
                    if w in adj[y] and y in adj[w]:
                        if (y, w) not in directed and (w, y) not in directed:
                            if not (w in adj[x] and x in adj[w]):
                                R1.append((y, w))

        R2 = []
        for x in nodes:
            for y in nodes:
                if x == y or not (y in adj[x] and x in adj[y]):
                    continue
                if (x, y) in directed or (y, x) in directed:
                    continue
                for z in nodes:
                    if z == x or z == y:
                        continue
                    if (x, z) in directed and (y, z) in directed:
                        R2.append((x, y))

        R3 = []
        for x in nodes:
            for y in nodes:
                for z in nodes:
                    if x == y or y == z or x == z:
                        continue
                    if (x, y) not in directed or (x, z) not in directed:
                        continue
                    if not (y in adj[z] and z in adj[y]):
                        continue
                    for w in nodes:
                        if w == x or w == y or w == z:
                            continue
                        if (z, w) in directed:
                            if not (w in adj[y] and y in adj[w]):
                                R3.append((z, w))

        for (u, v) in R1 + R2 + R3:
            if (u, v) not in directed and (v, u) not in directed:
                directed.add((u, v))
                changed = True

    return sorted((u, v) for (u, v) in directed)


@dataclass
class ConstraintSkeletonConfig(Config):
    n_nodes: int = 4
    n_ci: int = 2
    extra_sep: bool = False

    def apply_difficulty(self, level):
        self.n_nodes = int(4 + level // 2)
        self.n_ci = int(2 + level)
        self.extra_sep = level >= 3


def _fmt(edge):
    return f"V{edge[0]}->V{edge[1]}"


def _is_consistent_dag(n, answer):
    """True if the directed edge set is a valid DAG (no bidirectional edge, acyclic)."""
    fwd = {}
    for (u, v) in answer:
        if (v, u) in answer:
            return False
        fwd.setdefault(u, set()).add(v)
    order, seen = [], set()
    visiting = set()

    def visit(x):
        if x in visiting:
            return False
        if x in seen:
            return True
        visiting.add(x)
        for y in fwd.get(x, ()):
            if not visit(y):
                return False
        visiting.discard(x)
        seen.add(x)
        order.append(x)
        return True

    for x in range(n):
        if x not in seen:
            if not visit(x):
                return False
    return True


class ConstraintBasedSkeletonOrientation(Task):
    summary = ("Constraint-based skeleton search from listed conditional independencies: "
               "remove edges licensed by separations while recording separating sets, "
               "orient v-structures, apply Meek rules; answer the final edge set.")
    design_choice = ("Represent the skeleton as an undirected graph over a fixed node "
                     "set, and the answer is the canonical list of directed edges after "
                     "applying Meek rules.")
    config_cls = ConstraintSkeletonConfig

    def generate_entry(self):
        n = self.config.n_nodes
        n_ci = self.config.n_ci
        nodes = list(range(n))

        all_pairs = [(x, y) for x in range(n) for y in range(x + 1, n)]
        answer = []
        ci_triples = []
        for _attempt in range(400):
            a, b = random.sample(nodes, 2)
            a, b = sorted((a, b))
            collider_pool = [w for w in nodes if w != a and w != b]
            w = random.choice(collider_pool)
            rest = [x for x in nodes if x != a and x != b and x != w]
            if self.config.extra_sep:
                k = random.randrange(len(rest) + 1)
                sep = tuple(sorted(random.sample(rest, k)))
            else:
                sep = ()
            ci_triples = [(a, b, sep)]

            used_pairs = {(a, b)}
            blocked = {(a, w), (b, w), (w, a), (w, b)}
            avail = [(x, y) for (x, y) in all_pairs
                     if (x, y) not in used_pairs and (x, y) not in blocked]
            random.shuffle(avail)
            for (x, y) in avail[: n_ci - 1]:
                rp = [i for i in nodes if i != x and i != y]
                k = random.randrange(len(rp) + 1)
                s = tuple(sorted(random.sample(rp, k)))
                ci_triples.append((x, y, s))
                used_pairs.add((x, y))

            ci_triples = sorted(ci_triples)
            answer = _run_pc(n, ci_triples)
            if _is_consistent_dag(n, answer):
                break

        ci_lines = []
        for (x, y, s) in ci_triples:
            sep_str = ",".join(f"V{v}" for v in s) if s else "none"
            ci_lines.append(f"I(V{x};V{y} | {sep_str})")

        metadata = {
            "nodes": nodes,
            "n_nodes": n,
            "ci_triples": [[int(x), int(y), [int(v) for v in s]] for (x, y, s) in ci_triples],
            "answer": [_fmt(e) for e in answer],
        }
        ans_str = ";".join(metadata["answer"]) if answer else "none"
        return Entry(metadata=metadata, answer=ans_str)

    def render_prompt(self, metadata):
        node_str = ", ".join(f"V{v}" for v in metadata["nodes"])
        ci = ""
        for (a, b, sep) in sorted(tuple(t) for t in metadata["ci_triples"]):
            sep_str = ",".join(f"V{s}" for s in sep) if sep else "none"
            ci += f"  I(V{a};V{b} | {sep_str})\n"
        return (
            "We run a constraint-based (PC) skeleton and orientation search on the node "
            f"set {{{node_str}}}. The observed conditional independencies are:\n{ci}"
            "Each I(X;Y | S) states X and Y are conditionally independent given the "
            "separating set S, so the undirected edge X--Y is removed from the full "
            "skeleton and S is recorded as its separating set. Orient every "
            "v-structure X -> Z <- Y (non-adjacent X and Y with a common neighbor Z that "
            "is not in the separating set of X,Y), then complete the orientation with "
            "the Meek rules (R1: X->Y, Y--W, X and W non-adjacent => Y->W; "
            "R2: X->Z, Y->Z, X and Y adjacent => X->Y; R3: X->Y, X->Z, Y--Z, Z->W, "
            "Y and W non-adjacent => Z->W). List every directed edge of the final DAG "
            "as SRC->DST, separated by semicolons, sorted by source then destination. "
            "Answer: none if no directed edge remains."
        )

    def score_answer(self, answer, entry):
        gold_lines = entry.metadata["answer"]
        if answer is None:
            return 0.0
        if isinstance(answer, str):
            answer = answer.strip()
        else:
            answer = str(answer)
        if not gold_lines:
            return 1.0 if answer.lower() == "none" else 0.0
        parts = [p.strip() for p in answer.replace(",", ";").split(";") if p.strip()]
        norm = set()
        for p in parts:
            if "->" not in p:
                return 0.0
            u, v = p.split("->")
            u = u.strip()
            v = v.strip()
            if not u or not v:
                return 0.0
            norm.add((u, v))
        gold = set()
        for g in gold_lines:
            u, v = g.split("->")
            gold.add((u.strip(), v.strip()))
        return 1.0 if norm == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'constraint_based_skeleton_orientation (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_multi_relation_integration_r5/constraint_based_skeleton_orientation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
