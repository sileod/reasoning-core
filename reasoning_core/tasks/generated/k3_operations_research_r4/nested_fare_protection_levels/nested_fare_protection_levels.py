import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'nested_fare_protection_levels (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_operations_research_r4/nested_fare_protection_levels',
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

DESIGN_CHOICE = (
    "Answers are the availability count (cumulative booking limit) for a single "
    "specified fare class."
)

_CLASS_NAMES = ["J", "C", "D", "I", "Z"]
_CABIN_NAMES = ["first", "business", "premium economy"]


def _fractile_poisson(lam):
    """Smallest q>=0 with P(X>q) <= 0.5 for X~Poisson(lam) (the median fractile).

    q = min{n : P(X<=n) >= 0.5}. Following the guide, a verifier that can give
    up must reject; the iterative CDF sums to full probability mass so it always
    terminates.
    """
    if lam <= 0:
        return 0
    p = 2.718281828459045 ** (-lam)
    cum = p
    k = 0
    while cum < 0.5:
        k += 1
        p = p * (lam / k)
        cum += p
    return k


def _nested_limits(lams, cap):
    """Cumulative nested booking limits per class (monotone non-decreasing)."""
    lims = []
    running = 0
    for k in range(len(lams)):
        running += lams[k]
        lim = _fractile_poisson(running)
        lims.append(lim)
    # enforce monotone non-decreasing and a hard capacity ceiling
    out = []
    prev = 0
    for lim in lims:
        cur = max(prev, min(lim, cap))
        out.append(cur)
        prev = cur
    return out


@dataclass
class NestedFareProtectionConfig(Config):
    n_classes: int = 3
    cap: int = 40
    max_lam: int = 20

    def apply_difficulty(self, level):
        self.n_classes = 2 + int(level * 0.5)
        self.cap = 15 + int(level * 12)
        self.max_lam = 8 + int(level * 6)


class NestedFareProtectionLevels(Task):
    summary = ("Nested single-leg fare protection: given descending fares and "
               "independent Poisson demands sharing a cabin, report the nested "
               "booking-limit availability count for one specified fare class, "
               "taking each class's cumulative demand to its median fractile "
               "where expected marginal revenue meets the next fare down.")
    config_cls = NestedFareProtectionConfig
    design_choice = DESIGN_CHOICE

    def generate_entry(self):
        c = self.config.n_classes
        names = _CLASS_NAMES[:c]
        fares = sorted((random.randint(200, 2000) for _ in range(c)),
                       reverse=True)
        lams = [random.randint(1, self.config.max_lam) for _ in range(c)]
        lims = _nested_limits(lams, self.config.cap)
        target = random.randrange(c)
        answer = lims[target]
        if not (0 <= answer <= self.config.cap):
            raise RuntimeError("booking limit out of domain")
        metadata = {
            "cabins": [random.choice(_CABIN_NAMES)],
            "fares": fares,
            "lams": lams,
            "names": names,
            "bl": lims,
            "target": target,
            "target_name": names[target],
            "cap": self.config.cap,
        }
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        rows = "".join(
            "  {n}: fare {f}, demand Poisson(mean {l})\n".format(
                n=n, f=f, l=l)
            for n, f, l in zip(metadata["names"], metadata["fares"],
                               metadata["lams"])
        )
        cabin = metadata["cabins"][0]
        return (
            "A {cabin}-cabin aircraft fares nested fare classes on one leg of "
            "total capacity {cap}. Fares are ordered high to low as listed, the "
            "top class highest. Daily demand for each class is independent and "
            "Poisson-distributed with the given mean:\n"
            "{rows}"
            "Using single-leg expected-marginal-seat-revenue nesting, the airline "
            "sets each class's cumulative booking limit (the number of seats made "
            "available to that class) at the median fractile of the pooled demand "
            "of all classes at least as expensive as it: the smallest q with "
            "P(Poisson(pooled mean) > q) <= 0.5.\n"
            "What is the availability count -- the nested booking limit -- for "
            "class {target}? Answer a single non-negative integer."
        ).format(cabin=cabin, cap=metadata["cap"], rows=rows,
                 target=metadata["target_name"])

    def score_answer(self, answer, entry):
        a = _parse_int(answer)
        if a is None:
            return 0.0
        return 1.0 if a == int(entry.answer) else 0.0


def _parse_int(s):
    s = s.strip()
    if not s:
        return None
    try:
        return int(s)
    except Exception:
        return None
