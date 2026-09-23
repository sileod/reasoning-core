import heapq
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'prufer_coding (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_state_tracking_r4/prufer_coding',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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


def _prufer_decode(n, seq):
    degree = [1] * (n + 1)
    degree[0] = 0
    for x in seq:
        degree[x] += 1
    leaves = [v for v in range(1, n + 1) if degree[v] == 1]
    heapq.heapify(leaves)
    edges = []
    for x in seq:
        leaf = heapq.heappop(leaves)
        edges.append(tuple(sorted((leaf, x))))
        degree[leaf] -= 1
        degree[x] -= 1
        if degree[x] == 1:
            heapq.heappush(leaves, x)
    edges.append(tuple(sorted(leaves)))
    return frozenset(edges)


def _prufer_encode(n, edges):
    degree = [0] * (n + 1)
    adj = {v: set() for v in range(1, n + 1)}
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1
        adj[a].add(b)
        adj[b].add(a)
    leaves = [v for v in range(1, n + 1) if degree[v] == 1]
    heapq.heapify(leaves)
    seq = []
    for _ in range(n - 2):
        leaf = heapq.heappop(leaves)
        neighbor = next(iter(adj[leaf]))
        seq.append(neighbor)
        adj[leaf].remove(neighbor)
        adj[neighbor].remove(leaf)
        degree[leaf] -= 1
        degree[neighbor] -= 1
        if degree[neighbor] == 1:
            heapq.heappush(leaves, neighbor)
    return tuple(seq)


@dataclass
class PruferCodingV1Config(Config):
    n_min: int = 3
    n_max: int = 5

    def apply_difficulty(self, level):
        lo = 3 + level * 2
        hi = min(20, 5 + level * 3)
        self.n_min = min(lo, max(3, hi - 2))
        self.n_max = hi


class PruferCoding(Task):
    summary = "Encode a labeled tree, over 3 to 20 vertices 1..n, into its Prufer code by repeatedly stripping the smallest available leaf and appending its neighbor; answer is the code word as a space-separated list of integers."
    design_choice = "Vary tree size from 3 to 20 nodes; answer is Prufer sequence as a space-separated list of integers."
    config_cls = PruferCodingV1Config
    task_version = 2

    def generate_entry(self):
        n = random.randint(self.config.n_min, self.config.n_max)
        seq = tuple(random.randint(1, n) for _ in range(n - 2))
        edges = _prufer_decode(n, seq)
        assert _prufer_encode(n, edges) == seq, "Prufer round-trip failed"
        return Entry(metadata={"n": n, "edges": sorted(edges), "seq": list(seq)},
                     answer=" ".join(map(str, seq)))

    def render_prompt(self, metadata):
        n = metadata["n"]
        edges = ", ".join(f"({a},{b})" for a, b in sorted(metadata["edges"]))
        return (
            f"A labeled tree has vertices 1 through {n}. "
            f"Its undirected edges are: {edges}. "
            "The Prufer code of a labeled tree is built by repeatedly removing the leaf with the "
            "smallest remaining label and appending the label of its unique neighbor, until two "
            "vertices remain; the code has length n-2. "
            f"Compute the Prufer code of this tree and report it as a space-separated list of "
            "integers in the exact order the algorithm produces. "
            "Format example: 2 3 1. Give only the code."
        )

    def score_answer(self, answer, entry):
        try:
            tokens = [int(t) for t in str(answer).split()]
        except (TypeError, ValueError):
            return 0.0
        gold = [int(t) for t in str(entry.answer).split()]
        return 1.0 if tokens == gold else 0.0
