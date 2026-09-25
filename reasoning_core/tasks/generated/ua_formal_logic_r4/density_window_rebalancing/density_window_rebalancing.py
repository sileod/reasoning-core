import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class DensityWindowConfig(Config):
    n_min: int = 10
    n_max: int = 14
    k_min: int = 3
    k_max: int = 4

    def apply_difficulty(self, level):
        self.n_min = 10 + 3 * level
        self.n_max = 14 + 3 * level
        self.k_min = 3 + level // 2
        self.k_max = 4 + level // 2


_FRACTIONS = [0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.66, 0.7, 0.75, 0.8]


def _bounds(k, a, b):
    lo = int(a * k + 1e-9)
    if abs(a * k - round(a * k)) > 1e-9:
        lo = int(a * k) + 1
    hi = int(b * k + 1e-9)
    lo = max(0, lo)
    hi = min(k, hi)
    return lo, hi


def _max_kept(bits, k, lo, hi):
    n = len(bits)
    R = sum(bits)
    dp = {(tuple(), 0): 0}
    for i in range(n):
        ndp = {}
        for (W, total), pay in dp.items():
            for b in (0, 1):
                if total + b > R:
                    continue
                nW = W + (b,)
                if len(nW) == k:
                    if not (lo <= sum(nW) <= hi):
                        continue
                    nW = nW[1:]
                key = (nW, total + b)
                npay = pay + (1 if (b == 1 and bits[i] == 1) else 0)
                if npay > ndp.get(key, -1):
                    ndp[key] = npay
        dp = ndp
    best = -1
    for (W, total), pay in dp.items():
        if total == R and pay > best:
            best = pay
    return best


def _min_moves(bits, k, a, b):
    lo, hi = _bounds(k, a, b)
    kept = _max_kept(bits, k, lo, hi)
    if kept < 0:
        return None
    return sum(bits) - kept


def flatten_frac(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


class DensityWindowRebalancing(Task):
    summary = (
        "Generate a gapped ordered array under fixed-window density bounds a..b "
        "(occupied fraction per size-k window); find the minimal number of record "
        "moves so every sliding window's occupied count lies in [ceil(a*k), floor(b*k)]; "
        "answer is a single non-negative integer (0 means already valid)."
    )
    design_choice = (
        "Answer as a single integer: the minimal number of records to move so that "
        "every window of fixed size k has density between a and b."
    )
    config_cls = DensityWindowConfig

    def generate_entry(self):
        cfg = self.config
        for _ in range(300):
            n = random.randint(cfg.n_min, cfg.n_max)
            k = random.randint(cfg.k_min, cfg.k_max)
            if n < k + 2:
                continue
            candidates = [x for x in _FRACTIONS if x > 0.1]
            a = random.choice(candidates)
            b_choices = [x for x in _FRACTIONS if x > a]
            if not b_choices:
                continue
            b = random.choice(b_choices)
            if _bounds(k, a, b)[1] < _bounds(k, a, b)[0]:
                continue
            lo, hi = _bounds(k, a, b)
            target = random.uniform(max(lo / k, 0.0), min(hi / k, 1.0))
            bits = [1 if random.random() < target else 0 for _ in range(n)]
            moves = _min_moves(bits, k, a, b)
            if moves is None:
                continue
            answer = int(moves)
            payload = {
                "n": n,
                "k": k,
                "a": a,
                "b": b,
                "records": [i for i, v in enumerate(bits) if v],
            }
            entry = Entry(metadata=payload, answer=str(answer))
            return entry
        raise RuntimeError("density_window_rebalancing: failed to generate instance")

    def render_prompt(self, metadata):
        p = dict(metadata)
        records = p["records"]
        occ = "".join("X" if i in p["records"] else "." for i in range(p["n"]))
        a = flatten_frac(p["a"])
        b = flatten_frac(p["b"])
        return (
            f"An ordered array of {p['n']} cells is gapped; a record occupies cells "
            f"{records}. A window is any {p['k']} consecutive cells. Every window must "
            f"have density (occupied cells divided by {p['k']}) between {a} and {b}. "
            f"You may move a record from one cell to an empty cell, one record per move, "
            f"never changing the total number of records. What is the minimum number of "
            f"moves so that every {p['k']}-window satisfies the density bound? "
            f"Layout: {occ}. The answer is a single non-negative integer."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        gold = getattr(entry, "answer", None)
        return 1.0 if str(answer).strip() == str(gold) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'density_window_rebalancing (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/density_window_rebalancing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
