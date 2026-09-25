import random
from dataclasses import dataclass
from itertools import product

from reasoning_core.template import Config, Entry, Reward, Task


@dataclass
class FrustratedConfig(Config):
    num_sites: int = 3
    domain: int = 3
    num_pairs: int = 3
    num_high: int = 1
    bias: int = 2
    pinned: int = 1

    def apply_difficulty(self, level):
        self.num_sites = 3 + (level >= 2) + (level >= 4) + (level >= 6)
        self.domain = 2 + (level >= 1) + (level >= 3) + (level >= 5)
        self.num_pairs = 2 + (level >= 1) + (level >= 2) + (level >= 4)
        self.num_high = (level >= 5)
        self.bias = 1 + (level >= 2) + (level >= 4)
        self.pinned = (level >= 3)


def _parse_answer(answer):
    try:
        return int(str(answer).strip())
    except (ValueError, TypeError):
        return None


def _table_string(tbl):
    keys = sorted(tbl.keys())
    return "{" + ", ".join("{}: {}".format(k, tbl[k]) for k in keys) + "}"


class FrustratedGroundStatesEnergy(Task):
    summary = "Minimize total energy for finite-valued sites with competing pairwise and higher-order interactions, external biases, and pinned values; answer the minimum energy or site values shared by every minimizer."
    config_cls = FrustratedConfig

    def generate_entry(self):
        c = self.config
        n = c.num_sites
        d = c.domain
        domain_vals = list(range(1, d + 1))

        pinned_at = None
        pinned_val = None
        use_pinned = False
        if c.pinned:
            pinned_at = random.randrange(n)
            pinned_val = random.randint(1, d)
            use_pinned = True

        bias_terms = []
        for _ in range(c.bias):
            site = random.randrange(n)
            weights = [random.choice([-4, -2, -1, 1, 2, 3]) + random.randint(-2, 4)
                       for _ in range(d)]
            bias_terms.append((site, weights))

        pair_terms = []
        for _ in range(c.num_pairs):
            a, b = random.sample(range(n), 2)
            table = [[random.randint(-6, 6) for _ in range(d)] for _ in range(d)]
            pair_terms.append((a, b, table))

        high_terms = []
        if c.num_high and n >= 3:
            for _ in range(c.num_high):
                triple = tuple(sorted(random.sample(range(n), 3)))
                tbl = {"".join(map(str, combo)): random.randint(-8, 8)
                       for combo in product(range(d), repeat=3)}
                high_terms.append((triple, tbl))

        instance = {
            "domain": domain_vals,
            "pinned_at": pinned_at,
            "pinned_val": pinned_val,
            "bias": [(s, [int(v) for v in w]) for s, w in bias_terms],
            "pairs": [(a, b, [[int(v) for v in row] for row in tbl])
                      for a, b, tbl in pair_terms],
            "high": [(tuple(t), dict(tbl)) for t, tbl in high_terms],
        }

        feasible = [a for a in product(domain_vals, repeat=n)
                    if not (use_pinned and a[pinned_at] != pinned_val)]
        if not feasible:
            raise RuntimeError("no feasible assignment (over-pinned)")

        minima = []
        for a in feasible:
            e = 0
            for s, w in bias_terms:
                e += w[a[s] - 1]
            for a2, b2, tbl in pair_terms:
                e += tbl[a[a2] - 1][a[b2] - 1]
            for t, tbl in high_terms:
                e += tbl["".join(map(str, (a[i] - 1 for i in t)))]
            minima.append(e)
        min_val = min(minima)

        fixed = []
        for i in range(n):
            vals = {a[i] for a in feasible
                    if _assignment_energy(a, instance) == min_val}
            if len(vals) == 1:
                fixed.append((i, int(vals.pop())))

        metadata = dict(instance)
        metadata["n"] = n
        metadata["d"] = d
        metadata["energy"] = int(min_val)
        metadata["pinned_site"] = pinned_at
        metadata["shared"] = fixed
        return Entry(metadata=metadata, answer=str(int(min_val)))

    def render_prompt(self, metadata):
        domain_vals = sorted(metadata["domain"])
        n = metadata["n"]
        lines = []
        lines.append(
            "Each of the {} sites takes an integer value from the set {}. "
            "The total energy is the sum of:".format(n, domain_vals))
        lines.append("- a unary bias term per listed site, indexed by that site's value")
        lines.append("  bias terms: " + ", ".join(
            "b[{}]={}".format(s, w) for s, w in metadata["bias"]))
        lines.append("- a pairwise table for each listed pair, indexed by the two sites' values")
        lines.append("  pair tables: " + ", ".join(
            "p({},{})={}".format(a, b, tbl) for a, b, tbl in metadata["pairs"]))
        if metadata["high"]:
            lines.append("- a higher-order table for each listed triple, indexed by the three sites' values")
            lines.append("  triple tables: " + ", ".join(
                "h{}={}".format(t, _table_string(tbl)) for t, tbl in metadata["high"]))
        if metadata.get("pinned_site") is not None:
            lines.append("Site {} is pinned to value {} (it must equal that value).".format(
                metadata["pinned_site"], metadata["pinned_val"]))
        lines.append(
            "Find the minimum possible total energy over all assignments that respect any pinned "
            "site. The answer is that minimum energy, a single integer. Write only the integer.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        parsed = _parse_answer(answer)
        if parsed is None:
            return Reward(0.0, "not-an-integer")
        if parsed == entry.metadata["energy"]:
            return Reward(1.0, "correct")
        return Reward(0.0, "wrong")

    def distractor_candidates(self, entry):
        e = entry.metadata["energy"]
        cands = set()
        for off in (-7, -4, -2, -1, 1, 2, 3, 5, 7, 8, 11, 13):
            cands.add(str(e + off))
        cands.discard(str(e))
        return list(cands)[:6]


def _assignment_energy(assign, instance):
    e = 0
    for s, w in instance["bias"]:
        e += w[assign[s] - 1]
    for a, b, tbl in instance["pairs"]:
        e += tbl[assign[a] - 1][assign[b] - 1]
    for t, tbl in instance["high"]:
        e += tbl["".join(map(str, (assign[i] - 1 for i in t)))]
    return e


TASK_META = {'parent_source_id': None,
 'idea': 'frustrated_interaction_ground_states (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r4/frustrated_interaction_ground_states',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
