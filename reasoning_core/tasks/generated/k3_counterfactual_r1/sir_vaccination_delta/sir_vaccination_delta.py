import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'sir_vaccination_delta (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/sir_vaccination_delta',
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


@dataclass
class SirVaccinationDeltaConfig(Config):
    base_nodes: int = 6
    max_degree: int = 3
    seed_count: int = 1
    recovery: int = 2
    fraction: float = 0.2

    def apply_difficulty(self, level):
        self.base_nodes = 6 + 2 * level
        self.max_degree = 3 if level < 3 else 4
        self.seed_count = 1 + level // 2
        self.recovery = 2 + (1 if level >= 3 else 0) + (1 if level >= 5 else 0)


def _run(adj, immunized, seeds, recovery):
    immunized = set(immunized)
    remaining = {}
    ever = set()
    for s in seeds:
        if s not in immunized:
            remaining[s] = recovery
            ever.add(s)
    infected_sets = []
    while True:
        cur = {v for v in remaining if remaining[v] >= 1}
        infected_sets.append(cur)
        newly = []
        for v in range(len(adj)):
            if v in remaining or v in immunized or v in ever:
                continue
            for nb in adj[v]:
                if nb in cur:
                    newly.append(v)
                    break
        for v in list(remaining):
            remaining[v] -= 1
            if remaining[v] <= 0:
                del remaining[v]
        for v in newly:
            remaining[v] = recovery
            ever.add(v)
        if not remaining:
            break
    return ever, infected_sets


def _first_differing_day(sets_a, sets_b):
    length = max(len(sets_a), len(sets_b))
    for t in range(length):
        sa = sets_a[t] if t < len(sets_a) else set()
        sb = sets_b[t] if t < len(sets_b) else set()
        if sa != sb:
            return t
    return None


class SirVaccinationDelta(Task):
    summary = ("Run deterministic discrete-time SIR spread on a small contact graph, then "
               "immunize chosen nodes before day zero; answer both runs' final infection sizes "
               "and the first day the infected sets differ.")
    design_choice = ("Immunization set is a fixed fraction of the graph, count derived from graph "
                     "size to vary difficulty.")
    config_cls = SirVaccinationDeltaConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(80):
            n = cfg.base_nodes
            order = list(range(n))
            random.shuffle(order)
            adj = [set() for _ in range(n)]
            for i in range(1, n):
                a, b = order[i], order[i - 1]
                adj[a].add(b)
                adj[b].add(a)
            extra = random.randrange(0, cfg.max_degree * 2)
            for _ in range(extra):
                a, b = random.sample(range(n), 2)
                adj[a].add(b)
                adj[b].add(a)
            adj = [sorted(adj[v]) for v in range(n)]

            count = max(1, int(round(cfg.fraction * n)))
            immunized = sorted(random.sample(range(n), count))
            candidates = [v for v in range(n) if v not in immunized]
            if len(candidates) < cfg.seed_count:
                continue
            seeds = sorted(random.sample(candidates, cfg.seed_count))

            ever_a, sets_a = _run(adj, set(), seeds, cfg.recovery)
            ever_b, sets_b = _run(adj, immunized, seeds, cfg.recovery)

            impacted = [v for v in immunized if v in ever_a]
            if not impacted:
                continue
            if not ever_b:
                continue
            first_day = _first_differing_day(sets_a, sets_b)
            if first_day is None:
                continue

            final_a = len(ever_a)
            final_b = len(ever_b)
            assert isinstance(final_a, int) and 0 <= final_a <= n
            assert isinstance(final_b, int) and 0 <= final_b <= n
            assert isinstance(first_day, int) and first_day >= 0
            assert final_b < final_a

            answer = "%d %d %d" % (final_a, final_b, first_day)
            metadata = {
                "graph": adj,
                "seeds": seeds,
                "recovery": cfg.recovery,
                "immunized": immunized,
                "final_runA": final_a,
                "final_runB": final_b,
                "first_diff_day": first_day,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("SirVaccinationDelta: could not produce a satisfying instance")

    def render_prompt(self, metadata):
        g = metadata["graph"]
        n = len(g)
        edge_parts = []
        for i in range(n):
            if not g[i]:
                continue
            edge_parts.append("%d connected to %s" % (i, ", ".join(map(str, g[i]))))
        edge_text = "; ".join(edge_parts)
        seeds = ", ".join(map(str, metadata["seeds"]))
        imm = ", ".join(map(str, metadata["immunized"]))
        r = metadata["recovery"]
        return (
            "A population is modeled as a contact graph with nodes 0..%d. "
            "Edges: %s. "
            "On day 0 exactly these nodes are infectious: %s. An infectious node stays "
            "infectious for %d consecutive days, then becomes immune. On each day, every "
            "susceptible, non-immune node that has at least one currently-infectious neighbor "
            "becomes infectious the following day.\n"
            "Run this SIR process twice from the same day-0 infections. In run A, immunize no "
            "one. In run B, before day 0, permanently remove (immunize) these nodes so they can "
            "never be infected: [%s].\n"
            "Give three integers separated by spaces: the total number of distinct nodes ever "
            "infected in run A, then the same total for run B, then the smallest day index "
            "t>=0 at which run A's and run B's currently-infectious node sets first differ "
            "(day 0 is the seed day). Format example: '5 3 2'."
            % (n - 1, edge_text, seeds, r, imm)
        )

    def score_answer(self, answer, entry):
        parsed = _parse_answer(answer)
        if parsed is None:
            return 0.0
        gold = _parse_answer(entry.answer)
        return 1.0 if parsed == gold else 0.0


def _parse_answer(answer):
    if answer is None:
        return None
    parts = answer.strip().split()
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None
