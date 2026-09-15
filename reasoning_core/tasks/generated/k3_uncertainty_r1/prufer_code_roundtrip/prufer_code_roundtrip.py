import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'prufer_code_roundtrip (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_uncertainty_r1/prufer_code_roundtrip',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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


def meta_edges(edges):
    return [tuple(int(x) for x in e) for e in edges]


def code_str(code):
    return ", ".join(str(int(x)) for x in code)


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def tree_to_prufer(edges, n):
    degree = [0] * (n + 1)
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
        adj[u].append(v)
        adj[v].append(u)
    leaves = [v for v in range(1, n + 1) if degree[v] == 1]
    leaves.sort()
    code = []
    for _ in range(n - 2):
        leaf = leaves.pop(0)
        neigh = adj[leaf][0]
        code.append(neigh)
        degree[neigh] -= 1
        adj[neigh].remove(leaf)
        if degree[neigh] == 1:
            leaves.append(neigh)
            leaves.sort()
    return code


def rooted_parent(edges, n, root=1):
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = [None] * (n + 1)
    parent[root] = root
    stack = [root]
    while stack:
        cur = stack.pop()
        for nb in adj[cur]:
            if parent[nb] is None:
                parent[nb] = cur
                stack.append(nb)
    return parent


def random_tree(n):
    edges = []
    for v in range(2, n + 1):
        p = random.randint(1, v - 1)
        edges.append((v, p))
    return edges


def rebuild_edges_from_prufer(pr, n):
    degree = [1] * (n + 1)
    for x in pr:
        degree[x] += 1
    pr = list(pr)
    edges = []
    for i in range(n - 2):
        for v in range(1, n + 1):
            if degree[v] == 1:
                leaf = v
                break
        edges.append((leaf, pr[0]))
        degree[pr[0]] -= 1
        degree[leaf] -= 1
        pr.pop(0)
    rest = [v for v in range(1, n + 1) if degree[v] == 1]
    edges.append(tuple(sorted((rest[0], rest[1]))))
    return sorted(tuple(sorted(e)) for e in edges)


@dataclass
class PruferConfig(Config):
    n_low: int = 4
    n_high: int = 6

    def apply_difficulty(self, level):
        self.n_low = 4 + level
        self.n_high = 6 + level + stochastic_rounding(level)


class PruferCodeRoundtrip(Task):
    summary = "Translate a labeled tree to its Prüfer code by repeated smallest-leaf removal, then answer a queried code position, the parent of a queried vertex, or the rebuilt edge set."
    config_cls = PruferConfig
    design_choice = "Queried output is a single integer: the i-th Prüfer code entry for a given tree, with vertices labeled 1..n."

    QUERY_KINDS = ("position", "parent", "edges")

    def generate_entry(self):
        n = random.randint(self.config.n_low, self.config.n_high)
        code = []
        kind = random.choice(self.QUERY_KINDS)
        answer = None
        i = None
        q = None
        edges_sorted = []
        while answer is None:
            n = random.randint(self.config.n_low, self.config.n_high)
            edges = random_tree(n)
            edges_sorted = sorted(tuple(sorted(e)) for e in edges)
            code = tree_to_prufer(edges_sorted, n)
            kind = random.choice(self.QUERY_KINDS)
            if kind == "position":
                if n < 3:
                    continue
                i = random.randint(0, len(code) - 1)
                answer = str(code[i])
            elif kind == "parent":
                q = random.randint(2, n)
                parent = rooted_parent(edges_sorted, n, root=1)
                answer = str(parent[q])
            else:
                answer = ";".join(f"{u}-{v}" for u, v in edges_sorted)

        return Entry(
            metadata={
                "n": n,
                "edges": [list(e) for e in edges_sorted],
                "code": [int(x) for x in code],
                "kind": kind,
                "i": i,
                "q": q,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        n = metadata["n"]
        edges_str = ", ".join(f"{u}-{v}" for u, v in meta_edges(metadata["edges"]))
        kind = metadata["kind"]
        if kind == "position":
            i = metadata["i"]
            return (
                f"Consider the tree on vertices 1..{n} with edges {{{edges_str}}}. "
                f"A labeled tree can be encoded as its Prüfer code by the rule: at each step, "
                f"remove the smallest-labeled leaf and append its neighbor to the code, repeating "
                f"until only two vertices remain. What is the {ordinal(i + 1)} entry of the Prüfer "
                f"code of this tree? Answer with a single integer."
            )
        if kind == "parent":
            q = metadata["q"]
            return (
                f"Consider the tree on vertices 1..{n} with edges {{{edges_str}}}. Treat vertex 1 "
                f"as the root and orient every edge away from it, so each other vertex has a unique "
                f"parent. What is the parent vertex of vertex {q} in this rooted tree? "
                f"Answer with a single integer."
            )
        return (
            f"Consider the tree on vertices 1..{n} whose Prüfer code (built by repeated removal of "
            f"the smallest leaf, appending its neighbor) is [{code_str(metadata['code'])}]. "
            f"Rebuild the tree from this code and list all its edges. Give every edge as "
            f"u-v with u<v, edges separated by semicolons in lexicographic order."
        )

    def score_answer(self, answer, entry):
        kind = entry.metadata["kind"]
        answer = answer.strip()
        if kind == "edges":
            if not answer:
                return 0.0
            try:
                parts = [p for p in answer.split(";") if p]
                edges = []
                for p in parts:
                    u, v = p.split("-")
                    edges.append(tuple(sorted((int(u), int(v)))))
                edges = sorted(edges)
                target = [tuple(sorted(e)) for e in entry.metadata["edges"]]
                return 1.0 if edges == target else 0.0
            except Exception:
                return 0.0
        try:
            return 1.0 if int(answer) == int(entry.answer) else 0.0
        except Exception:
            return 0.0
