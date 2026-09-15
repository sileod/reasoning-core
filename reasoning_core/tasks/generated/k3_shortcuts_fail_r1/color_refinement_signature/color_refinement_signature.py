import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'color_refinement_signature (draw 2 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/color_refinement_signature',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 241712510,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}

design_choice = "Use graphs with up to 20 vertices and inject adversarial near-isomorphic pairs (e.g., CFI gadgets) to force many refinement rounds."


def _refine(colors, adj):
    n = len(adj)
    sigs = [None] * n
    for v in range(n):
        sigs[v] = (colors[v], tuple(sorted(colors[u] for u in adj[v])))
    order = sorted(range(n), key=lambda v: sigs[v])
    newcol = [0] * n
    cur = 0
    for idx, v in enumerate(order):
        if idx and sigs[v] != sigs[order[idx - 1]]:
            cur += 1
        newcol[v] = cur
    return newcol


def _partition_from_colors(colors):
    classes = {}
    for v, c in enumerate(colors):
        classes.setdefault(c, []).append(v)
    return sorted((sorted(cls) for cls in classes.values()), key=lambda cls: cls[0])


def stable_partition(adj):
    n = len(adj)
    colors = [0] * n
    while True:
        new = _refine(colors, adj)
        if new == colors:
            break
        colors = new
    return _partition_from_colors(colors)


def encode_partition(classes):
    return ";".join(" ".join(str(v) for v in cls) for cls in classes)


def _colors_from_classes(classes):
    colors = [0] * sum(len(cls) for cls in classes)
    for i, cls in enumerate(classes):
        for v in cls:
            colors[v] = i
    return colors


def _verify(classes, adj):
    n = len(adj)
    flat = [v for cls in classes for v in cls]
    assert sorted(flat) == list(range(n)), "partition must cover all vertices exactly"
    assert all(cls for cls in classes), "every color class must be non-empty"
    colors = _colors_from_classes(classes)
    colors2 = _refine(colors, adj)
    assert encode_partition(_partition_from_colors(colors2)) == encode_partition(classes), (
        "claimed stable partition must be a fixed point of one refinement round")


def _empty(n):
    return [[] for _ in range(n)]


def _path(n):
    adj = [[] for _ in range(n)]
    for v in range(n):
        if v > 0:
            adj[v].append(v - 1)
        if v < n - 1:
            adj[v].append(v + 1)
    return adj


def _cycle(n):
    adj = [[] for _ in range(n)]
    for v in range(n):
        adj[v].append((v - 1) % n)
        adj[v].append((v + 1) % n)
    return adj


def _complete(n):
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                adj[i].append(j)
    return adj


def _random_tree(n):
    adj = [[] for _ in range(n)]
    for v in range(1, n):
        p = random.randrange(v)
        adj[v].append(p)
        adj[p].append(v)
    return adj


def _random_graph(n, p):
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                adj[i].append(j)
                adj[j].append(i)
    return adj


def _twin_graph(n, twin_prob):
    if twin_prob and random.random() < twin_prob:
        base = _random_tree(n - 1)
    else:
        base = _random_graph(n - 1, 0.45)
    base.append([])
    u = random.randrange(n - 1)
    for x, nbrs in enumerate(base):
        if x == u:
            continue
        if u in nbrs:
            nbrs.append(n - 1)
            base[n - 1].append(x)
    base[u].append(n - 1)
    base[n - 1].append(u)
    return base


@dataclass
class ColorRefinementConfig(Config):
    max_vertices: int = 8
    twin_prob: float = 0.0

    def apply_difficulty(self, level):
        self.max_vertices = min(20, 8 + 2 * level)
        self.twin_prob = min(0.5, 0.18 + 0.06 * level)


class ColorRefinementSignature(Task):
    summary = "Recolor graph vertices by the sorted multiset of neighbor colors until the partition stabilizes; graphs range over random graphs, trees, paths, symmetric regular graphs, and twin-adversarial near-isomorphic traps with up to 20 vertices; answer the stable color partition."
    config_cls = ColorRefinementConfig

    def generate_entry(self):
        max_n = self.config.max_vertices
        style = random.random()
        if self.config.twin_prob and random.random() < self.config.twin_prob and max_n >= 3:
            n = random.randint(3, max_n)
            adj = _twin_graph(n, self.config.twin_prob)
        elif style < 0.25:
            n = random.randint(2, max_n)
            adj = _random_graph(n, random.uniform(0.2, 0.6))
        elif style < 0.55:
            n = random.randint(2, max_n)
            adj = _random_tree(n)
        elif style < 0.75:
            n = random.randint(3, max_n)
            adj = _path(n)
        elif style < 0.88:
            if max_n >= 3:
                n = random.randint(3, max_n)
                adj = _cycle(n)
            else:
                n = random.randint(2, max_n)
                adj = _random_tree(n)
        else:
            if max_n >= 2:
                n = random.randint(2, min(6, max_n))
            else:
                n = 1
            if n < 2:
                adj = _empty(1)
            else:
                adj = _complete(n)

        classes = stable_partition(adj)
        _verify(classes, adj)
        adjacency_sorted = [sorted(nbrs) for nbrs in adj]
        answer = encode_partition(classes)
        return Entry(
            metadata={"adjacency": adjacency_sorted, "n": len(adj)},
            answer=answer,
        )

    def render_prompt(self, metadata):
        lines = "\n".join(
            f"{i}: {' '.join(map(str, nbrs))}"
            for i, nbrs in enumerate(metadata["adjacency"])
        )
        return (
            "Perform the standard color refinement (1-dimensional Weisfeiler-Leman) on the "
            "following undirected graph. Give every vertex the same starting color 0. Then "
            "repeat a refinement round: the new color of a vertex is determined by its own "
            "color together with the sorted multiset of its neighbors' colors, and two "
            "vertices keep the same color exactly when both their own colors and their "
            "sorted neighbor-color multisets are identical; relabel the resulting classes "
            "as new colors arbitrarily. Stop once a full round changes nothing. The final "
            "stable coloring partitions the vertices into color classes.\n"
            "\n"
            f"Vertices are the integers 0..{metadata['n'] - 1}, listed with their neighbors:\n"
            f"{lines}\n"
            "\n"
            "Give the final stable color partition as the canonical list of its classes. "
            "Write each class as its vertex numbers in ascending order and list the classes "
            "in ascending order of their first vertex. Join the vertices within a class with "
            "a single space and separate the classes with a semicolon. For example, if "
            "vertices {0,3} share one color and vertices {1,2,4,5} share another, the "
            "answer is:\n"
            "0 3;1 2 4 5"
        )
