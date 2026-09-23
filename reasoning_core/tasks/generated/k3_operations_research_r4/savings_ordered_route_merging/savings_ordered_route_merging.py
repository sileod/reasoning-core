import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SavingsConfig(Config):
    n_customers: int = 5
    max_demand: int = 8
    capacity: int = 15
    max_coord: int = 30

    def apply_difficulty(self, level):
        self.n_customers = max(4, int(4 + 2 * level))
        self.max_demand = int(5 + 1 * level)
        self.capacity = max(10, int(14 + 3 * level))
        self.max_coord = int(20 + 8 * level)


TASK_META = {'parent_source_id': None,
 'idea': 'savings_ordered_route_merging (variant 1 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/savings_ordered_route_merging',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2305351643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _endpoint_savings(ra, rb, d00, dij):
    a0, a1 = ra[0], ra[-1]
    b0, b1 = rb[0], rb[-1]
    choices = [
        (d00[a1] + d00[b0] - dij[a1][b0], (ra, rb)),
        (d00[a0] + d00[b1] - dij[a0][b1], (_reverse(ra), _reverse(rb))),
    ]
    return max(choices, key=lambda t: t[0])


def _reverse(seq):
    return list(reversed(seq))


def _run_savings(demands, coords, capacity, depot):
    n = len(demands)
    d00 = [_dist(coords[i], depot) for i in range(n)]
    dij = [[_dist(coords[i], coords[j]) for j in range(n)] for i in range(n)]

    routes = []
    for i in range(n):
        routes.append([i])

    for _ in range(n * n):
        best_key = None
        bi = bj = None
        for x in range(len(routes)):
            for y in range(x + 1, len(routes)):
                ra = routes[x]
                rb = routes[y]
                if sum(demands[v] for v in ra) + sum(demands[v] for v in rb) > capacity:
                    continue
                sav, (nra, nrb) = _endpoint_savings(ra, rb, d00, dij)
                key = (-sav, min(ra), min(rb), tuple(ra), tuple(rb))
                if best_key is None or key < best_key:
                    best_key = key
                    bi, bj = x, y
        if best_key is None:
            break
        ra, rb = routes[bi], routes[bj]
        _, (nra, nrb) = _endpoint_savings(ra, rb, d00, dij)
        newr = nra + nrb
        routes[bi] = newr
        routes.pop(bj)

    seen = set()
    final = []
    for r in routes:
        canon = frozenset(r)
        if canon in seen:
            continue
        seen.add(canon)
        final.append(r)
    final.sort(key=lambda r: (min(r), tuple(r)))
    return final


class SavingsOrderedRouteMerging(Task):
    summary = "Merge single-stop routes by descending depot savings under capacity, joining only at route ends and flipping orientation as needed; answers are the final routes, total distance, or which profitable merge was blocked first."
    design_choice = "Instance format: a list of customer demands and coordinates, with a depot at origin and a fixed vehicle capacity; the solver must output the final route set as ordered customer-ID sequences."
    config_cls = SavingsConfig
    task_version = 2

    def generate_entry(self):
        c = self.config
        n = c.n_customers
        while True:
            demands = [random.randint(1, c.max_demand) for _ in range(n)]
            if max(demands) <= c.capacity:
                break
        coords = [(random.randint(-c.max_coord, c.max_coord),
                   random.randint(-c.max_coord, c.max_coord)) for _ in range(n)]
        depot = (0, 0)

        final = _run_savings(demands, coords, c.capacity, depot)

        assert len(final) == len({frozenset(r) for r in final})
        for r in final:
            assert len(set(r)) == len(r)
            if len(r) > 1:
                assert sum(demands[x] for x in r) <= c.capacity
        assert all(0 <= a < n for r in final for a in r)
        covered = set()
        for r in final:
            covered.update(r)
        assert covered == set(range(n))

        route_strings = ["-".join(str(x) for x in r) for r in final]
        answer = " | ".join(route_strings)

        return Entry(metadata={
            "demands": [int(d) for d in demands],
            "coords": [[int(x) for x in p] for p in coords],
            "depot": [0, 0],
            "capacity": int(c.capacity),
            "routes": [[int(x) for x in r] for r in final],
        }, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        lines.append("A depot sits at the origin (0, 0).")
        lines.append(f"Vehicle capacity is {metadata['capacity']}.")
        for i, (d, (x, y)) in enumerate(zip(metadata["demands"], metadata["coords"])):
            lines.append(f"Customer {i} has demand {d} at ({x}, {y}).")
        prompt = "\n".join(lines)
        prompt += (
            "\n\nBegin with one single-customer route per customer. Repeatedly consider all "
            "remaining pairs of routes in decreasing order of the savings d(0,i)+d(0,j)-d(i,j) "
            "where i is one endpoint of the first route and j one endpoint of the second route; "
            "use the pair giving the largest such savings (ties broken by smaller first-id then "
            "smaller second-id of the two routes, then shorter first route, then shorter second "
            "route), flip route orientations as needed so the two endpoints meet, and join the "
            "routes end-to-end whenever the sum of their demands does not exceed capacity; skip "
            "a pair whose combined demand exceeds capacity. Stop when no capacity-feasible pair "
            "improves by merging. Give the final routes as ordered customer-ID sequences: IDs "
            "joined by '-' in travel order, routes separated by ' | ', e.g. '1-2-3 | 0'."
        )
        return prompt

    def score_answer(self, answer, entry):
        return 1.0 if answer.strip() == entry.answer.strip() else 0.0
