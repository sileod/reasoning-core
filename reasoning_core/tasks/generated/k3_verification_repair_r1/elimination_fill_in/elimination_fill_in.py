import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class EliminationFillInConfig(Config):
    nodes: int = 5
    edge_prob: float = 0.5

    def apply_difficulty(self, level):
        self.nodes = stochastic_rounding(self.nodes + level * 2)
        self.edge_prob = min(0.75, self.edge_prob + 0.03 * level)


def _fill_edges(nodes, order, adjacency):
    edges = set()
    adj = {u: set(adjacency[u]) for u in range(nodes)}
    for v in order:
        nbrs = [u for u in adj[v] if u in adj]
        for i in range(len(nbrs)):
            for j in range(i + 1, len(nbrs)):
                a, b = nbrs[i], nbrs[j]
                if a != b and b not in adj[a]:
                    edges.add((min(a, b), max(a, b)))
                    adj[a].add(b)
                    adj[b].add(a)
        adj.pop(v, None)
    return sorted(edges)


def _largest_clique(nodes, adjacency):
    best = 0
    vertices = list(range(nodes))
    for mask in range(1 << nodes):
        if bin(mask).count("1") <= best:
            continue
        ok = True
        chosen = [v for v in vertices if (mask >> v) & 1]
        for i in range(len(chosen)):
            for j in range(i + 1, len(chosen)):
                if chosen[j] not in adjacency[chosen[i]]:
                    ok = False
                    break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            best = bin(mask).count("1")
    return best


class EliminationFillIn(Task):
    summary = ("Eliminate vertices in a stated order while completing each current "
               "neighborhood into a clique by added fill edges; answer with the "
               "sorted list of fill edges, its size, or the largest clique formed by "
               "any elimination step.")
    config_cls = EliminationFillInConfig
    design_choice = ("Present the elimination order in the prompt; solver must compute "
                     "and list all added fill edges as canonical unordered pairs.")
    task_version = 2

    def generate_entry(self):
        n = self.config.nodes
        order = list(range(n))
        random.shuffle(order)
        adjacency = [set() for _ in range(n)]
        for u in range(n):
            for v in range(u + 1, n):
                if random.random() < self.config.edge_prob:
                    adjacency[u].add(v)
                    adjacency[v].add(u)
        edges = _fill_edges(n, order, adjacency)
        largest = 0
        current = [set(adjacency[u]) for u in range(n)]
        for v in order:
            nbrs = [u for u in current[v] if current[u]]
            cand = len(nbrs) + 1
            if cand > largest:
                largest = cand
            for u in list(current[v]):
                current[u].discard(v)
            current[v] = set()
        largest_dynamic = largest
        fill_size = len(edges)
        mode = random.choice(["list", "size", "largest"])
        if mode == "list":
            answer = "none" if not edges else ";".join(f"{a}-{b}" for a, b in edges)
            prompt = (f"An undirected graph on vertices 0..{n - 1} has edges "
                      f"{_fmt_edges(adjacency)}. We eliminate vertices in the order "
                      f"{order}. Eliminating a vertex adds fill edges to make its "
                      "current neighborhood a clique. What is the complete sorted list "
                      "of added fill edges as unordered pairs a-b, separated by "
                      "semicolons? If none are added, answer with 'none'.")
        elif mode == "size":
            answer = str(fill_size)
            prompt = (f"An undirected graph on vertices 0..{n - 1} has edges "
                      f"{_fmt_edges(adjacency)}. We eliminate vertices in the order "
                      f"{order}. Eliminating a vertex adds fill edges to make its "
                      "current neighborhood a clique. How many fill edges are added in "
                      "total? Answer with the count.")
        else:
            answer = str(largest_dynamic)
            prompt = (f"An undirected graph on vertices 0..{n - 1} has edges "
                      f"{_fmt_edges(adjacency)}. We eliminate vertices in the order "
                      f"{order}. Eliminating a vertex makes its current neighborhood "
                      "(including the vertex) into a clique. What is the size of the "
                      "largest clique formed during any elimination step? Answer with "
                      "the integer.")

        return Entry(metadata={"nodes": n, "order": order,
                               "adjacency": [sorted(a) for a in adjacency],
                               "fill_edges": [list(e) for e in edges],
                               "fill_size": fill_size,
                               "largest_clique": largest_dynamic,
                               "mode": mode},
                     answer=answer)

    def render_prompt(self, metadata):
        n = metadata["nodes"]
        adj = [set(a) for a in metadata["adjacency"]]
        order = metadata["order"]
        mode = metadata["mode"]
        if mode == "list":
            return (f"An undirected graph on vertices 0..{n - 1} has edges "
                    f"{_fmt_edges(adj)}. We eliminate vertices in the order "
                    f"{order}. Eliminating a vertex adds fill edges to make its "
                    "current neighborhood a clique. What is the complete sorted list "
                    "of added fill edges as unordered pairs a-b, separated by "
                    "semicolons? If none are added, answer with 'none'.")
        elif mode == "size":
            return (f"An undirected graph on vertices 0..{n - 1} has edges "
                    f"{_fmt_edges(adj)}. We eliminate vertices in the order "
                    f"{order}. Eliminating a vertex adds fill edges to make its "
                    "current neighborhood a clique. How many fill edges are added in "
                    "total? Answer with the count.")
        else:
            return (f"An undirected graph on vertices 0..{n - 1} has edges "
                    f"{_fmt_edges(adj)}. We eliminate vertices in the order "
                    f"{order}. Eliminating a vertex makes its current neighborhood "
                    "(including the vertex) into a clique. What is the size of the "
                    "largest clique formed during any elimination step? Answer with "
                    "the integer.")

    def score_answer(self, answer, entry):
        mode = entry.metadata["mode"]
        expected = entry.answer
        answer = (answer or "").strip()
        if not answer:
            return 0.0
        if mode == "list":
            try:
                if expected == "none":
                    return 1.0 if answer == "none" else 0.0
                got = {tuple(sorted(map(int, p.split("-")))) for p in answer.split(";")}
                exp = {tuple(e) for e in entry.metadata["fill_edges"]}
                return 1.0 if got == exp else 0.0
            except Exception:
                return 0.0
        try:
            return 1.0 if int(answer) == int(expected) else 0.0
        except Exception:
            return 0.0


def _fmt_edges(adjacency):
    pairs = []
    for u in range(len(adjacency)):
        for v in adjacency[u]:
            if u < v:
                pairs.append(f"{u}-{v}")
    return "[]" if not pairs else "{" + ", ".join(pairs) + "}"


TASK_META = {'parent_source_id': None,
 'idea': 'elimination_fill_in (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/elimination_fill_in',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
