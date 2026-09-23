import ast
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'facility_member_swap_descent (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/facility_member_swap_descent',
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

design_choice = ("Answer as an ordered list of swap tuples (member_id, candidate_id), "
                 "final facility set, and integer total cost, with ties broken by "
                 "smallest member_id then smallest candidate_id.")


@dataclass
class FacilitySwapConfig(Config):
    clients: int = 5
    sites: int = 6
    k: int = 3
    coord_range: int = 20

    def apply_difficulty(self, level):
        self.clients = 5 + int(1.4 * level)
        self.sites = 6 + int(1.8 * level)
        self.k = 3 + int(0.5 * level)
        self.coord_range = 20 + 8 * level
        if self.k < 1:
            self.k = 1
        if self.sites <= self.k:
            self.k = max(1, self.sites - 1)


def _manhattan(p, q):
    return abs(p[0] - q[0]) + abs(p[1] - q[1])


def _cost(F, clients, sites):
    total = 0
    for cx, cy in clients:
        best = min(_manhattan((cx, cy), sites[i]) for i in F)
        total += best
    return total


def _best_swap(F, cost, clients, site_ids, sites):
    closed = [i for i in site_ids if i not in F]
    best_key = None
    for out in sorted(F):
        for inn in closed:
            c2 = _cost((F - {out}) | {inn}, clients, sites)
            imp = cost - c2
            if imp > 0:
                key = (-imp, out, inn)
                if best_key is None or key < best_key:
                    best_key = key
    return best_key


def _parse_answer(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s.startswith('swaps='):
        return None
    try:
        rest = s[len('swaps='):]
        swaps_part, rest = rest.split('; set=', 1)
        set_part, cost_part = rest.split('; cost=', 1)
        seq = ast.literal_eval(swaps_part)
        final = ast.literal_eval(set_part)
        cost = ast.literal_eval(cost_part)
    except Exception:
        return None
    if not isinstance(seq, list) or not isinstance(final, list):
        return None
    if not isinstance(cost, int) or cost < 0:
        return None
    try:
        norm_seq = tuple(tuple(int(x) for x in t) for t in seq)
        norm_final = tuple(sorted(int(x) for x in final))
    except Exception:
        return None
    if len(norm_seq) != len(seq) or len(norm_final) != len(final):
        return None
    return (norm_seq, norm_final, cost)


class FacilityMemberSwapDescent(Task):
    summary = ("From a chosen facility set, evaluate every member-out/candidate-in swap's "
               "exact change in nearest-facility distance, apply the best improving swap, "
               "repeat to local optimum; answers are swap sequence, final set, and cost.")
    config_cls = FacilitySwapConfig

    def _attempt(self):
        C = self.config
        nm, nc, k = C.clients, C.sites, C.k
        R = C.coord_range
        if k < 1 or nc <= k or nm < 1 or nc < 2:
            return None
        site_ids = list(range(nc))
        sites = {i: (random.randint(0, R), random.randint(0, R)) for i in site_ids}
        clients = [(random.randint(0, R), random.randint(0, R)) for _ in range(nm)]
        initial = sorted(random.sample(site_ids, k))
        F = set(initial)
        cost = _cost(F, clients, sites)
        seq = []
        steps = 0
        while steps < 100000:
            key = _best_swap(F, cost, clients, site_ids, sites)
            if key is None:
                break
            _, out, inn = key
            seq.append((out, inn))
            F = (F - {out}) | {inn}
            cost = cost + key[0]
            steps += 1
        final = sorted(F)
        answer = "swaps=%r; set=%r; cost=%d" % (seq, final, cost)
        return Entry(metadata={
            'k': k,
            'clients': [[x, y] for x, y in clients],
            'sites': [[x, y] for i in site_ids for x, y in (sites[i],)],
            'initial': initial,
            'seq': [[a, b] for a, b in seq],
            'final_set': final,
            'cost': cost,
        }, answer=answer)

    def generate_entry(self):
        for _ in range(300):
            entry = self._attempt()
            if entry is not None:
                return entry
        raise RuntimeError("facility_member_swap_descent: could not generate a valid instance")

    def render_prompt(self, metadata):
        k = metadata['k']
        clients_str = "\n".join("C%d: (%d,%d)" % (i, x, y)
                                for i, (x, y) in enumerate(metadata['clients']))
        sites_str = "\n".join("%d: (%d,%d)" % (i, x, y)
                              for i, (x, y) in enumerate(metadata['sites']))
        return (
            "We open exactly %d of the listed facility sites and serve every client from its "
            "nearest open site (Manhattan distance |dx|+|dy|). The currently open sites form "
            "the member set. A steepest-descent local search is run from that set: in each step, "
            "pick one member site (the one removed) and one closed site (the one added) such that "
            "the swap lowers the total client-to-nearest-open-site distance the most; break ties "
            "by smallest member id then smallest candidate id; apply that swap and record "
            "(member_id, candidate_id). Repeat until no swap lowers the cost (local optimum).\n"
            "\n"
            "Clients (grid points):\n%s\n\n"
            "Facility sites (id: (x, y)):\n%s\n\n"
            "Current member set: %s\n"
            "\n"
            "Report the swaps applied (in order), the final member set, and the integer total "
            "cost at the local optimum, exactly as: swaps=[(m,c),(m,c)]; set=[id,...]; cost=N\n"
            "For example: swaps=[(1,5),(2,3)]; set=[1,2,3]; cost=17"
        ) % (k, clients_str, sites_str, repr(metadata['initial']))

    def score_answer(self, answer, entry):
        g = _parse_answer(entry.answer)
        c = _parse_answer(answer)
        if g is None or c is None:
            return 0.0
        return 1.0 if c == g else 0.0
