import random
import sys
from dataclasses import dataclass
from math import factorial

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'linear_extension_counting (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_inference_modes_r4/linear_extension_counting',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
                                         'version': 'bubblewrap 0.8.0'}}}}


def _transitive_closure(edges, n):
    reach = [[False] * n for _ in range(n)]
    for u, v in edges:
        reach[u][v] = True
    for k in range(n):
        rk = reach[k]
        for i in range(n):
            ri = reach[i]
            if not ri[k]:
                continue
            for j in range(n):
                if rk[j]:
                    ri[j] = True
    return reach


def _covering_pairs(reach, n):
    cover = []
    for u in range(n):
        for v in range(n):
            if u == v or not reach[u][v]:
                continue
            transitive = False
            for w in range(n):
                if w != u and w != v and reach[u][w] and reach[w][v]:
                    transitive = True
                    break
            if not transitive:
                cover.append((u, v))
    return cover


def _count_linear_extensions(reach, n):
    full = (1 << n) - 1
    memo = [0] * (full + 1)
    memo[0] = 1
    for S in range(1, full + 1):
        total = 0
        s = S
        while s:
            bit = s & -s
            x = bit.bit_length() - 1
            maximal = True
            ys = S
            while ys:
                b = ys & -ys
                y = b.bit_length() - 1
                if y != x and reach[x][y]:
                    maximal = False
                    break
                ys -= b
            if maximal:
                total += memo[S ^ bit]
            s -= bit
        memo[S] = total
    return memo[full]


def _random_tree_cover(n):
    children = {v: [] for v in range(n)}
    cover = []
    for i in range(1, n):
        parent = random.randint(0, i - 1)
        cover.append((parent, i))
        children[parent].append(i)
    return cover


def _hook_length_count(cover, n):
    children = {v: [] for v in range(n)}
    for u, v in cover:
        children[u].append(v)
    is_child = {v for _, v in cover}
    roots = [r for r in range(n) if r not in is_child]
    size = [0] * n
    sys.setrecursionlimit(10000)

    def dfs(v):
        s = 1
        for c in children[v]:
            s += dfs(c)
        size[v] = s
        return s

    for r in roots:
        dfs(r)
    prod = 1
    for s in size:
        prod *= s
    return factorial(n) // prod


def _generate_poset(n, density_min, density_max):
    density = random.uniform(density_min, density_max)
    target = max(1, int(round(density * n * (n - 1) / 2)))
    order = list(range(n))
    random.shuffle(order)
    pos = [0] * n
    for i, v in enumerate(order):
        pos[v] = i
    pairs = set()
    attempts = 0
    max_attempts = 4000
    while attempts < max_attempts:
        a, b = random.sample(range(n), 2)
        if pos[a] < pos[b]:
            u, v = a, b
        else:
            u, v = b, a
        pairs.add((u, v))
        reach = _transitive_closure(sorted(pairs), n)
        comparable = sum(1 for i in range(n) for j in range(i + 1, n)
                         if reach[i][j] or reach[j][i])
        attempts += 1
        if comparable >= target:
            return _transitive_closure(sorted(pairs), n)
    return _transitive_closure(sorted(pairs), n)


@dataclass
class LinearExtensionCountConfig(Config):
    min_n: int = 5
    max_n: int = 6
    density_min: float = 0.25
    density_max: float = 0.45
    tree_prob: float = 0.5

    def apply_difficulty(self, level):
        self.min_n = 5 + level
        self.max_n = 6 + level
        self.density_min = 0.25
        self.density_max = 0.45 + 0.05 * level


class LinearExtensionCountV1(Task):
    task_name = "linear_extension_count"
    summary = ("Count the linear extensions of a partial order by dynamic programming over its "
               "lattice of down-sets; answer the exact extension count, with trees handled by "
               "their hook-length product formula.")
    design_choice = ("Represent the partial order as a DAG of integer-labeled vertices, with "
                     "instances generated by random edge insertion until a fixed "
                     "transitive-reduction density is reached.")
    config_cls = LinearExtensionCountConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = random.randint(cfg.min_n, cfg.max_n)
        use_tree = random.random() < cfg.tree_prob

        if use_tree:
            cover = _random_tree_cover(n)
            reach = _transitive_closure(cover, n)
            dp_count = _count_linear_extensions(reach, n)
            hook_count = _hook_length_count(cover, n)
            if dp_count != hook_count:
                raise RuntimeError("hook-length and down-set DP disagree on a tree poset")
            count = dp_count
        else:
            reach = _generate_poset(n, cfg.density_min, cfg.density_max)
            cover = _covering_pairs(reach, n)
            count = _count_linear_extensions(reach, n)

        assert isinstance(count, int) and count >= 1, "extension count must be a positive integer"

        metadata = {
            "n": n,
            "type": "tree" if use_tree else "dag",
            "covering": [[int(u), int(v)] for u, v in cover],
            "answer": int(count),
        }
        return Entry(metadata=metadata, answer=str(int(count)))

    def render_prompt(self, metadata):
        cover = sorted((u, v) for u, v in metadata["covering"])
        relations = "; ".join(f"{u} < {v}" for u, v in cover)
        return (
            f"Consider the partial order on the vertex set {{0,...,{metadata['n'] - 1}}} whose "
            f"cover relations (each \"x < y\" means x is covered by y, i.e. x is below y with no "
            f"element between) are: {relations}. "
            f"A linear extension is a total ordering of all vertices that respects every "
            f"cover relation. Count the number of linear extensions of this partial order "
            f"by a down-set dynamic program (or, for trees, the hook-length product formula). "
            f"The answer is one non-negative integer: the exact number of linear extensions."
        )

    def score_answer(self, answer, entry):
        reference = entry["answer"]
        prepr = lambda x: str(x).strip()
        a, r = prepr(answer), prepr(reference)
        try:
            return 1.0 if int(a) == int(r) else 0.0
        except (ValueError, TypeError):
            return 0.0
