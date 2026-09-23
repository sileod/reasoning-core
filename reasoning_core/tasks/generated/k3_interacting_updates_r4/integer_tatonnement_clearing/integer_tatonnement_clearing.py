import random
import itertools
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'integer_tatonnement_clearing (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_interacting_updates_r4/integer_tatonnement_clearing',
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


@dataclass
class TatonnementConfig(Config):
    n_goods: int = 3
    steps: int = 3
    p_min: int = 1
    p_max: int = 5
    full_steps: int = 6
    target_step: int = 3

    def apply_difficulty(self, level):
        base_goods = 2
        self.n_goods = base_goods + int(level * 0.75)
        if level == 0:
            self.n_goods = 2
        self.steps = 3 + level
        self.p_min = 1
        self.p_max = 4 + level
        self.full_steps = 3 + level * 2
        self.target_step = max(0, (3 + level * 2) // 2)


def demand_sign(good, p_own, params):
    _, intercept, price, slope = params[good]
    demand = intercept - slope * p_own
    if demand > 0:
        return 1
    if demand < 0:
        return -1
    return 0


def update_prices(prices, params):
    signs = []
    for g in range(len(params)):
        signs.append(demand_sign(g, prices[g], params))
    newp = []
    for g in range(len(params)):
        np_ = prices[g] + signs[g]
        newp.append(max(1, np_))
    return tuple(newp)


def simulate(prices, params, steps):
    seq = [tuple(prices)]
    for _ in range(steps):
        prices = update_prices(prices, params)
        seq.append(tuple(prices))
    return seq


class IntegerTatonnementClearing(Task):
    summary = ("Adjust integer goods prices by the sign of excess demand while demands "
               "shift with budgets; answer prices at a queried step, the order in which "
               "markets clear, or whether the adjustment cycles forever.")
    design_choice = ("Represent prices as integer vectors and demands as piecewise-linear "
                     "functions of own-price only, with excess demand signs determining "
                     "unit price increments.")
    config_cls = TatonnementConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_goods
        bounds = (2, 8)
        mode = random.choice(["step", "order", "cycle"])

        attempts = 0
        while attempts < 100:
            attempts += 1
            params = []
            for _ in range(n):
                intercept = random.randint(1, bounds[1])
                slope = random.randint(1, bounds[1])
                price = random.randint(cfg.p_min, cfg.p_max)
                params.append((0, intercept, price, slope))
            price0t2 = tuple(random.randint(cfg.p_min, cfg.p_max) for _ in range(n))
            seq = simulate(price0t2, params, cfg.full_steps)
            if mode == "step":
                t = random.randint(0, cfg.target_step)
                ans = seq[t]
                metas = {"mode": "step", "t": t, "prices": ans}
                return self._make_entry(mode, params, price0t2, cfg, metas)
            if mode == "order":
                order = []
                visited = set()
                for step_idx in range(1, len(seq)):
                    for g in range(n):
                        s = demand_sign(g, seq[step_idx - 1][g], params)
                        if s == 0 and g not in visited:
                            order.append(g)
                            visited.add(g)
                if len(visited) >= 1:
                    ans = tuple(order)
                    metas = {"mode": "order", "order": list(ans)}
                    return self._make_entry(mode, params, price0t2, cfg, metas)
                continue
            if mode == "cycle":
                horizon = cfg.target_step + 1
                if len(seq) > horizon:
                    seqh = seq[:horizon]
                else:
                    seqh = seq
                cyc = len(set(seqh)) < len(seqh)
                ans = "yes" if cyc else "no"
                metas = {"mode": "cycle", "answer": ans}
                return self._make_entry(mode, params, price0t2, cfg, metas)

        raise RuntimeError("could not generate instance")

    def _make_entry(self, mode, params, price0, cfg, metas):
        metadata = {
            "n_goods": cfg.n_goods,
            "params": [list(p) for p in params],
            "prices0": list(price0),
            "p_min": cfg.p_min,
            "p_max": cfg.p_max,
            "mode": mode,
            "target_step": cfg.target_step,
        }
        metadata.update(metas)
        return Entry(metadata=metadata, answer=self._answer(mode, metadata))

    def _answer(self, mode, metadata):
        if mode == "cycle":
            return "yes" if metadata["answer"] == "yes" else "no"
        if mode == "step":
            return " ".join(str(x) for x in metadata["prices"])
        if mode == "order":
            return " ".join(str(g) for g in metadata["order"])

    def render_prompt(self, metadata):
        m = metadata
        lines = []
        for g in range(m["n_goods"]):
            _, intercept, _, slope = m["params"][g]
            lines.append(
                "good %d: demand = %d - %d*p_%d" % (g, intercept, slope, g))
        lines.append("initial prices: " + " ".join(str(x) for x in m["prices0"]))
        rules = ("At each step, for every good simultaneously, compare its own demand "
                 "to zero: if demand > 0 the price rises by 1; if demand < 0 it falls by 1; "
                 "if demand == 0 the price stays (that market has cleared). Prices never drop "
                 "below 1. Price changes are integer and unit-sized.")
        if m["mode"] == "step":
            lines.append("After the adjustment at step %d, what is the price of each good? "
                         "Answer %d integers giving good 0..%d in order, separated by spaces."
                         % (m["t"], m["n_goods"], m["n_goods"] - 1))
        elif m["mode"] == "order":
            lines.append("A market clears the first step at which its own demand is exactly 0 "
                         "(after the update). In what order do the markets clear? Give the good "
                         "indices that ever clear, in the order they first clear, as integers "
                         "separated by spaces.")
        else:
            lines.append("Within the first %d steps (counting the initial prices as step 0), "
                         "decide whether the price adjustment ever returns the goods to an "
                         "earlier price vector. Give the single word yes or no as your "
                         "answer." % (metadata["target_step"]))
        return "\n".join(lines[:2] + [rules] + lines[2:])

    def score_answer(self, answer, entry):
        m = entry.metadata
        mode = m["mode"]
        if mode == "cycle":
            return 1.0 if _norm_cycle(answer) == _norm_cycle(entry.answer) else 0.0
        return 1.0 if _norm(answer) == _norm(entry.answer) else 0.0


Tatonnement = IntegerTatonnementClearing


def _norm(s):
    if not isinstance(s, str):
        return " ".join(str(x) for x in s)
    return " ".join(s.split())


def _norm_cycle(s):
    if not isinstance(s, str):
        return "yes" if s else "no"
    return s.strip().lower()
