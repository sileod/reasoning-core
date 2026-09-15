import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'selinger_join_ordering (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_specific_r1/selinger_join_ordering',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _optimal_join_cost(adjacency, base):
    n = len(adjacency)
    full = (1 << n) - 1
    conn = [False] * (1 << n)
    for s in range(1 << n):
        if s == 0:
            conn[s] = True
            continue
        start = (s & -s).bit_length() - 1
        seen = 1 << start
        stack = [start]
        while stack:
            u = stack.pop()
            for nb, _ in adjacency[u]:
                if (s >> nb) & 1 and not ((seen >> nb) & 1):
                    seen |= (1 << nb)
                    stack.append(nb)
        conn[s] = (seen == s)
    prod = [1] * (1 << n)
    for s in range(1, 1 << n):
        lb = s & -s
        v = lb.bit_length() - 1
        prod[s] = prod[s ^ lb] * base[v]
    dp = [None] * (1 << n)
    dp[0] = 0
    for s in range(1, 1 << n):
        if not conn[s]:
            continue
        if s & (s - 1) == 0:
            dp[s] = 0
            continue
        bestcost = None
        sub = (s - 1) & s
        while sub:
            if conn[sub]:
                other = s ^ sub
                if conn[other]:
                    cost = dp[sub] + dp[other] + prod[s]
                    if bestcost is None or cost < bestcost:
                        bestcost = cost
            sub = (sub - 1) & s
        dp[s] = bestcost
    return dp[full]


@dataclass
class JoinOrderConfig(Config):
    n: int = 4
    max_card: int = 6
    density: float = 0.6

    def apply_difficulty(self, level):
        self.n = min(7, int(stochastic_rounding(self.n + level)))
        self.max_card = int(stochastic_rounding(6 + 2 * level))
        self.density = min(0.95, 0.6 + 0.05 * level)


class SelingerJoinOrdering(Task):
    summary = ("Compute the optimal join order for a query graph using Selinger dynamic "
               "programming with a given cost model; answer the optimal plan cost or tree.")
    design_choice = ("Represent the query graph as an adjacency list with cardinalities on "
                     "edges, and answer the minimum total cost as an integer after running "
                     "Selinger DP over all subsets.")
    config_cls = JoinOrderConfig
    task_version = 2

    def generate_entry(self):
        while True:
            n = self.config.n
            max_card = max(3, self.config.max_card)
            base = [random.randint(2, max_card) for _ in range(n)]
            adjacency = [[] for _ in range(n)]
            for u in range(n):
                for v in range(u + 1, n):
                    if random.random() < self.config.density:
                        c = random.randint(2, max_card)
                        adjacency[u].append([v, c])
                        adjacency[v].append([u, c])
            if any(len(a) == 0 for a in adjacency):
                continue
            cost = _optimal_join_cost(adjacency, base)
            if cost is None or cost < 0:
                continue
            metadata = {"n": n, "base": base, "adjacency": adjacency, "cost": cost}
            return Entry(metadata=metadata, answer=str(cost))

    def render_prompt(self, metadata):
        lines = []
        for u in range(metadata["n"]):
            nbrs = metadata["adjacency"][u]
            if nbrs:
                parts = ", ".join(f"{v}:{c}" for v, c in nbrs)
                lines.append(f"{u}: {parts}")
            else:
                lines.append(f"{u}:")
        graph = "; ".join(lines)
        return (
            f"We have {metadata['n']} relations in a join query. Each relation has base "
            f"cardinality given in order: {metadata['base']}. An edge (v:card) in the "
            f"adjacency list of a relation u denotes an equi-join between u and v with that "
            f"row-cardinality. The adjacency list is: {graph}. Using Selinger dynamic "
            f"programming over all subsets (the intermediate result of a set of joined "
            f"relations has cardinality equal to the product of the base cardinalities of "
            f"those relations), find the minimum total cost of assembling all relations into "
            f"a single join tree, where the cost of each join step is the cardinality of the "
            f"intermediate result it produces. Answer only the minimum total cost as an integer."
        )

    def score_answer(self, answer, entry):
        gold = entry.answer
        try:
            f = float(answer)
        except Exception:
            return 0.0
        if f == int(f) and abs(f - int(gold)) < 1e-9:
            return 1.0
        return 0.0
