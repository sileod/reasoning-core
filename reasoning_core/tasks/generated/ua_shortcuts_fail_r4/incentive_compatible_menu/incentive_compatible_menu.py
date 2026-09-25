"""Incentive-compatible menu design: revenue-maximizing truthful allocation with voluntary participation."""

import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class IncentiveMenuConfig(Config):
    level: int = 0
    max_dims: int = 1
    max_types: int = 2
    v_max: int = 2

    def apply_difficulty(self, level):
        self.level = min(int(level), 6)
        self.max_dims = 1 if self.level < 1 else 2
        self.max_types = 2 if self.level < 2 else 3
        self.v_max = 2 + self.level


def _value(v, bundle):
    return sum(a * b for a, b in zip(v, bundle))


def _optimal_payments(types, profile):
    """Greatest IC/IR-feasible integer price vector, or None if no feasible prices exist.

    The price constraints are only upper bounds: t_i <= value_i (IR) and
    t_i - t_j <= (value_i(x_i) - value_i(x_j)) (IC). Descent from the IR
    ceiling converges monotonically to the greatest feasible point in at
    most the total ceiling steps; a profile whose constraints are mutually
    contradictory (a negative-cost cycle) never settles and is None.
    """
    n = len(types)
    t = [_value(types[i], profile[i]) for i in range(n)]
    cap = sum(t) + 1
    for _ in range(cap):
        changed = False
        for i in range(n):
            best = t[i]
            own = _value(types[i], profile[i])
            for j in range(n):
                if j == i:
                    continue
                cand = t[j] + own - _value(types[i], profile[j])
                if cand < best:
                    best = cand
            if best < t[i]:
                t[i] = best
                changed = True
        if not changed:
            return t
    return None


def _max_profit(types, profile_cap, weights):
    """Exhaustive search over all feasible allocation profiles (each type one bundle)."""
    n = len(types)
    d = len(types[0])
    bundles = list(itertools.product((0, 1), repeat=d))
    best_profit = -1
    best_profile = None
    best_t = None
    for profile in itertools.product(bundles, repeat=n):
        if any(
            sum(profile[i][j] for i in range(n)) > profile_cap[j]
            for j in range(d)
        ):
            continue
        t = _optimal_payments(types, profile)
        if t is None:
            continue
        profit = sum(w * ti for w, ti in zip(weights, t))
        if profit > best_profit:
            best_profit = profit
            best_profile = profile
            best_t = t
    assert best_profile is not None, "empty allocation is always feasible"
    return best_profit, best_profile, best_t


def _parse_int(text):
    try:
        return int(str(text).strip())
    except (TypeError, ValueError):
        return None


class IncentiveCompatibleMenu(Task):
    summary = ("Optimize a menu of allocations and payments subject to truthful choice and "
               "voluntary participation; vary multidimensional valuations, type probabilities, "
               "and allocation restrictions; answer maximum expected profit.")
    config_cls = IncentiveMenuConfig
    design_choice = ("Instances vary in the number of types (2 vs 3) and allocation dimensions "
                     "(1 vs 2), with answer as exact integer profit.")

    def generate_entry(self):
        cfg = self.config
        n = random.randint(2, cfg.max_types)
        d = random.randint(1, cfg.max_dims)
        weights = [random.randint(1, 3) for _ in range(n)]
        types = [
            [random.randint(1, cfg.v_max) for _ in range(d)]
            for _ in range(n)
        ]
        caps = tuple(random.randint(1, n) for _ in range(d))
        profit, profile, prices = _max_profit(types, caps, weights)
        assert profit >= 0, "revenue cannot be negative"
        assert all(0 <= ti for ti in prices), "prices cannot be negative"

        metadata = {
            "types": n,
            "dims": d,
            "weights": weights,
            "valuations": types,
            "caps": caps,
            "price": prices,
            "allocation": [list(x) for x in profile],
            "profit": profit,
        }
        return Entry(metadata=metadata, answer=str(profit))

    def render_prompt(self, metadata):
        d = metadata["dims"]
        lines = []
        for i, v in enumerate(metadata["valuations"]):
            per = ", ".join(f"{v[j]} for good {j + 1}" for j in range(d))
            lines.append(
                f"Type {i + 1} makes up a weight w = {metadata['weights'][i]} and values "
                f"the goods at {per} per unit."
            )
        cap_line = ", ".join(
            f"at most {metadata['caps'][j]} copies of good {j + 1}" for j in range(d)
        )
        body = "\n".join(lines)
        return (
            "A seller designs an incentive-compatible, individually rational menu for "
            f"{metadata['types']} buyer types. There are {d} goods in unit supply; a bundle is a "
            f"{d}-vector of 0s and 1s marking which goods a buyer receives, and a type's value for a "
            "bundle is the sum of its per-unit values times the units of each good. "
            f"{body} Feasibility requires that {cap_line} are allocated in total across types. "
            "The seller picks one (bundle, price) outcome for each type; any type may instead take "
            "the outside option of the empty bundle at price 0. Truthfulness requires every type to "
            "weakly prefer its own outcome to every other offered outcome, including taking nothing, "
            "and participation is voluntary. The seller maximizes total revenue, the sum over types "
            "of the type's weight times its price. What is the maximum total revenue? "
            "The answer is a single non-negative integer."
        )

    def score_answer(self, answer, entry):
        gold = _parse_int(entry.answer)
        guess = _parse_int(answer)
        if gold is None or guess is None:
            return 0.0
        return 1.0 if guess == gold else 0.0


TASK_META = {
    'parent_source_id': None,
    'idea': 'incentive_compatible_menu (variant 1 of 3)',
    'hypothesis': 'P006',
    'changes': 'new task in reasoning_core/tasks/generated/ua_shortcuts_fail_r4/incentive_compatible_menu',
    'generation': {
        'provider_name': 'albert',
        'model_name': 'deepseek-v4-flash',
        'harness_name': 'opencode',
        'harness_version': '1.18.32',
        'agent_name': 'task-search-worker',
        'settings': {
            'variant': None,
            'requested_seed': 798610012,
            'seed_forwarded': True,
            'temperature': None,
            'top_p': None,
            'pure': True,
            'max_steps': 56,
            'timeout_seconds': 1800,
            'sandbox': {'name': 'bubblewrap', 'version': 'bubblewrap 0.8.0'},
        },
    },
}
