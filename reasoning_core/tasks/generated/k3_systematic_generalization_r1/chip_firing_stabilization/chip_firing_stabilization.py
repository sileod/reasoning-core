import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'chip_firing_stabilization (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/chip_firing_stabilization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _stabilize(adj, chips, cap=100000):
    state = list(chips)
    n = len(state)
    it = 0
    while True:
        fired = False
        for v in range(n):
            if state[v] >= len(adj[v]):
                d = len(adj[v])
                state[v] -= d
                for u in adj[v]:
                    state[u] += 1
                fired = True
                break
        if not fired:
            break
        it += 1
        if it > cap:
            return None
    return tuple(state)


def _is_stable(adj, state):
    for v in range(len(state)):
        if state[v] >= len(adj[v]):
            return False
    return True


def _normalize(s):
    if not isinstance(s, str):
        return None
    nums = re.findall(r"-?\d+", s)
    if not nums:
        return None
    return tuple(int(x) for x in nums)


def _canonical(entry):
    stable = _stabilize(entry.metadata["adj"], entry.metadata["chips"])
    return "[" + ", ".join(str(c) for c in stable) + "]"


@dataclass
class ChipFiringStabilizationConfig(Config):
    n: int = 5
    max_chips: int = 5

    def apply_difficulty(self, level):
        self.n = min(4 + level, 9)
        self.max_chips = 3 + level


class ChipFiringStabilization(Task):
    summary = ("Stabilize chip configurations on undirected graphs by firing overloaded "
               "vertices (chips to each neighbor) under sequential orders; return the "
               "stable vector, per-vertex firing tally, or prefix legality.")
    design_choice = ("Answer form: return only the final stable chip count vector, "
                     "with per-vertex totals omitted to force full stabilization computation.")
    config_cls = ChipFiringStabilizationConfig

    def generate_entry(self):
        n = self.config.n
        max_chips = self.config.max_chips
        while True:
            edges = []
            for u in range(n):
                for v in range(u + 1, n):
                    if random.random() < 0.4:
                        edges.append((u, v))
            deg = [0] * n
            for u, v in edges:
                deg[u] += 1
                deg[v] += 1
            if 0 in deg:
                continue
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            deg = [len(a) for a in adj]
            s = sum(deg) - n
            if s < 2:
                continue
            low = max(1, s // 2)
            total = random.randint(low, s - 1)
            chips = [0] * n
            for _ in range(total):
                chips[random.randrange(n)] += 1
            if all(chips[v] < deg[v] for v in range(n)):
                continue
            stable = _stabilize(adj, chips, cap=2000000)
            if stable is None or not _is_stable(adj, stable):
                continue
            for c in stable:
                assert isinstance(c, int) and c >= 0
            return Entry(metadata={"n": n, "edges": edges, "chips": chips, "adj": adj, "stable": stable},
                         answer="[" + ", ".join(str(c) for c in stable) + "]")

    def render_prompt(self, metadata):
        n = metadata["n"]
        edges = metadata["edges"]
        chips = metadata["chips"]
        edge_str = ", ".join(f"({u}, {v})" for u, v in edges)
        chip_str = ", ".join(str(c) for c in chips)
        return (f"We have an undirected graph on vertices 0..{n - 1} with edges "
                f"{{{edge_str}}}. The vertices 0..{n - 1} hold chips "
                f"[{chip_str}]. Repeatedly fire any vertex that has at least as many "
                f"chips as its degree: firing removes degree-many chips from it and "
                f"adds one chip to each of its neighbors. Continue until no vertex is "
                f"overloaded. Return the final stable chip vector for vertices "
                f"0..{n - 1}, as a list of integers like [a, b, c].")

    def score_answer(self, answer, entry):
        return 1.0 if _normalize(answer) == _normalize(entry.answer) else 0.0
