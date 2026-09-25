import math
import random
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linprog

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'coalitional_payoff_stability (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r4/coalitional_payoff_stability',
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
class CoalitionPayoffConfig(Config):
    n: int = 2
    bound_hi: int = 4
    n_coalitions: int = 1
    overlap: float = 0.0

    def apply_difficulty(self, level):
        self.n = min(6, 2 + level)
        self.bound_hi = 3 + 2 * level
        self.n_coalitions = 1 + level
        self.overlap = min(0.9, 0.2 * level)


def _lp(lo, hi, T, coalitions, fix=None):
    n = len(lo)
    A_ub = []
    b_ub = []
    for members, thr in coalitions:
        row = [0] * n
        for i in members:
            row[i] = -1
        A_ub.append(row)
        b_ub.append(-thr)
    A_eq = [[1] * n]
    b_eq = [T]
    if fix is not None:
        row = [0] * n
        row[fix[0]] = 1
        A_eq.append(row)
        b_eq.append(fix[1])
    return linprog(c=[0] * n, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                   bounds=list(zip(lo, hi)), method="highs")


def _feasible(lo, hi, T, coalitions):
    return bool(_lp(lo, hi, T, coalitions).success)


def _tight_range(lo, hi, T, coalitions):
    n = len(lo)
    cmin = [0] * n
    cmin[0] = 1.0
    cmax = [0] * n
    cmax[0] = -1.0
    A_ub = []
    b_ub = []
    for members, thr in coalitions:
        row = [0] * n
        for i in members:
            row[i] = -1
        A_ub.append(row)
        b_ub.append(-thr)
    A_eq = [[1] * n]
    b_eq = [T]
    rmin = linprog(c=cmin, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                   bounds=list(zip(lo, hi)), method="highs")
    rmax = linprog(c=cmax, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                   bounds=list(zip(lo, hi)), method="highs")
    lo0 = int(lo[0])
    hi0 = int(hi[0])
    start = max(lo0, int(math.floor(rmin.fun)))
    end = min(hi0, int(math.ceil(-rmax.fun)))
    vals = []
    for v in range(start, end + 1):
        if _lp(lo, hi, T, coalitions, fix=(0, v)).success:
            vals.append(v)
    return vals


def _coalitions(n, n_coal, overlap):
    used = set()
    result = []
    for _ in range(n_coal):
        if n >= 3 and random.random() < overlap:
            size = random.choice([2, 3])
            s = tuple(sorted(random.sample(range(n), min(size, n))))
        else:
            avail = sorted(set(range(n)) - used)
            if not avail:
                avail = sorted(range(n))
            size = random.choice([1, 2]) if n >= 2 else 1
            s = tuple(sorted(random.sample(avail, min(size, len(avail)))))
        if not s:
            s = (0,)
        result.append(s)
        used.update(s)
    return result


class CoalitionalPayoffStability(Task):
    summary = "Allocate a fixed surplus under overlapping coalitions' blocking thresholds, individual guarantees, and payoff caps; answer whether a stable allocation exists or the tight integer payoff range for one member."
    design_choice = "Vary coalition structures from disjoint groups to nested and overlapping sets, changing whether stability hinges on cross-coalition constraints or only on individual bounds."
    config_cls = CoalitionPayoffConfig
    task_version = 2

    def generate_entry(self):
        c = self.config
        for _ in range(60):
            n = c.n
            labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:n])
            lo = [random.randint(0, c.bound_hi // 2) for _ in range(n)]
            hi = [int(lo[i]) + random.randint(1, c.bound_hi) for i in range(n)]
            r = [int(random.randint(int(lo[i]), int(hi[i]))) for i in range(n)]
            T = sum(r)
            member_sets = _coalitions(n, c.n_coalitions, c.overlap)
            if random.random() < 0.5:
                mode = "range"
            else:
                mode = "exists"
            target = "yes" if random.random() < 0.5 else "no"
            if mode == "exists" and target == "no":
                thresholds = [sum(r[i] for i in s) for s in member_sets]
                j = random.randrange(len(member_sets))
                thresholds[j] = int(sum(hi[i] for i in member_sets[j])) + random.randint(1, 3)
                coalitions = list(zip(member_sets, thresholds))
                if not _feasible(lo, hi, T, coalitions):
                    return self._entry(labels, lo, hi, T, member_sets, thresholds, mode, "no")
                continue
            else:
                thresholds = []
                for s in member_sets:
                    sumr = sum(r[i] for i in s)
                    slack = random.randint(0, max(0, sumr))
                    thresholds.append(int(sumr - slack))
                coalitions = list(zip(member_sets, thresholds))
                if not _feasible(lo, hi, T, coalitions):
                    continue
                if mode == "exists":
                    return self._entry(labels, lo, hi, T, member_sets, thresholds, mode, "yes")
                vals = _tight_range(lo, hi, T, coalitions)
                if not vals:
                    continue
                answer = f"[{vals[0]}, {vals[-1]}]"
                return self._entry(labels, lo, hi, T, member_sets, thresholds, mode, answer)
        raise RuntimeError("could not construct a stable instance")

    def _entry(self, labels, lo, hi, T, member_sets, thresholds, mode, answer):
        return Entry(metadata={
            "labels": list(labels),
            "lo": [int(v) for v in lo],
            "hi": [int(v) for v in hi],
            "T": int(T),
            "member_sets": [list(s) for s in member_sets],
            "thresholds": [int(t) for t in thresholds],
            "mode": mode,
        }, answer=answer)

    def render_prompt(self, metadata):
        labels = metadata["labels"]
        n = len(labels)
        lo = metadata["lo"]
        hi = metadata["hi"]
        T = metadata["T"]
        member_sets = metadata["member_sets"]
        thresholds = metadata["thresholds"]
        head = (
            f"{n} players {', '.join(labels[:-1])} and {labels[-1]} divide a total surplus of {T}. "
            "Every player must receive at least its individual guarantee and at most its payoff cap:\n"
        )
        rows = []
        for i in range(n):
            rows.append(f"{labels[i]}: guarantee {lo[i]}, cap {hi[i]}")
        co_rows = []
        for s, t in zip(member_sets, thresholds):
            names = ", ".join(labels[i] for i in s)
            co_rows.append(f"{{{names}}}: {t}")
        body = (
            "The following coalitions each block any allocation whose combined payoff for their members is below the threshold shown:\n"
            + "\n".join(co_rows)
        )
        tail = (
            "A stable allocation satisfies every guarantee, every cap, the total {T} (all players receive exactly {T} together), and every coalition threshold."
        )
        if metadata["mode"] == "range":
            return (
                head + "\n".join(rows) + "\n\n" + body + "\n\n" + tail +
                f"\nGive the tight range of integer values {labels[0]} can receive in some stable allocation. "
                "Answer as a single bracket pair [lo, hi] with the two integers."
            )
        return (
            head + "\n".join(rows) + "\n\n" + body + "\n\n" + tail +
            f"\nDoes a stable allocation exist? Reply only with a single word: yes or no.\n"
            f"Does a stable allocation exist?"
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        ans = answer.strip()
        if entry.metadata["mode"] == "exists":
            return float(ans in ("yes", "no") and ans == entry.answer)
        return float(ans == entry.answer)
