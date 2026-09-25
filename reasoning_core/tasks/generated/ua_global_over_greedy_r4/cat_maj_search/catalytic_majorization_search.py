import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'catalytic_majorization_search (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r4/catalytic_majorization_search',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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

design_choice = "Answer as the minimum integer dimension d for which there exists a rational auxiliary vector with denominators \u2264 D, else 'none'"


def _compositions(total):
    for mask in range(1 << (total - 1)):
        parts = []
        start = 1
        for bit in range(total - 1):
            if mask & (1 << bit):
                parts.append(bit + 2 - start)
                start = bit + 2
        parts.append(total - start + 1)
        yield parts


def _tensor(w, y):
    return [wi * yj for wi in w for yj in y]


def _majorized_by(u, v):
    us = sorted(u, reverse=True)
    vs = sorted(v, reverse=True)
    if sum(us) != sum(vs):
        return False
    su = sv = Fraction(0)
    for k in range(len(us) - 1):
        su += us[k]
        sv += vs[k]
        if su > sv:
            return False
    return True


def _min_dim(w, x, D, fixed_last):
    best = None
    for parts in _compositions(D):
        if fixed_last is not None and parts[-1] != fixed_last:
            continue
        if best is not None and len(parts) >= best:
            continue
        y = [Fraction(p, D) for p in parts]
        if _majorized_by(_tensor(w, y), _tensor(x, y)):
            best = len(parts)
    return best


@dataclass
class CatMajConfig(Config):
    n: int = 2
    Q: int = 6
    D: int = 4

    def apply_difficulty(self, level):
        self.n = 2 + (1 if level >= 3 else 0)
        self.Q = 6 + 2 * level
        self.D = min(12, 4 + 2 * level)


class CatMajSearch(Task):
    summary = ("Find the minimum integer dimension d of a rational probability vector y "
               "whose entries are positive multiples of 1/D, optionally with one fixed "
               "coordinate, such that w\u2297y is majorized by x\u2297y for random "
               "distributions w and x; answer the minimum d or the word none.")
    config_cls = CatMajConfig
    task_version = 2

    @staticmethod
    def _composition(total, parts):
        cuts = sorted(random.sample(range(1, total), parts - 1))
        comps = [cuts[0]]
        for i in range(1, parts - 1):
            comps.append(cuts[i] - cuts[i - 1])
        comps.append(total - cuts[-1])
        return comps

    def generate_entry(self):
        cfg = self.config
        n, Q, D = cfg.n, cfg.Q, cfg.D
        while True:
            W = self._composition(Q, n)
            X = self._composition(Q, n)
            if W != X:
                break
        w = [Fraction(a, Q) for a in W]
        x = [Fraction(b, Q) for b in X]

        fixed_last = None
        if random.random() < 0.5:
            fixed_last = random.randint(1, D)

        d = _min_dim(w, x, D, fixed_last)
        answer = 'none' if d is None else str(d)
        assert answer == 'none' or (answer.isdigit() and 1 <= int(answer) <= D), answer

        metadata = {
            'w': [str(Fraction(a, Q)) for a in W],
            'x': [str(Fraction(b, Q)) for b in X],
            'numerator_w': W,
            'numerator_x': X,
            'n': n,
            'Q': Q,
            'D': D,
            'fixed_last': fixed_last,
            'dimension': d,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        w = ' '.join(metadata['w'])
        x = ' '.join(metadata['x'])
        D = metadata['D']
        n = metadata['n']
        if metadata['fixed_last'] is not None:
            fixed = ("The last coordinate of y is fixed, so a_d (the last of the a_i) "
                     "must equal %d." % metadata['fixed_last'])
        else:
            fixed = "No coordinate of y is fixed."
        return (
            "Two probability distributions over %d outcomes are w = %s and x = %s "
            "(entries are fractions of a common denominator). For a probability vector y "
            "whose entries are positive multiples of 1/%d summing to 1, write the tensor "
            "w\u2297y for the length %d\u00b7d vector of all pairwise products w_i * y_j. "
            "For two same-length vectors u and v, u is majorized by v, written u \u227a v, "
            "when, with u and v each sorted non-increasing, every leading partial sum of u "
            "is at most the corresponding leading partial sum of v and the totals are "
            "equal (Hardy-Littlewood-P\u00f3lya). A vector y is a catalyst for the "
            "relation w\u2297y \u227a x\u2297y when that relation holds, and the dimension "
            "of y is the number of its entries d, which ranges from 1 to %d. %s "
            "Find the minimum dimension d of a catalyst y, meaning the least d for which "
            "there exists such a y with w\u2297y \u227a x\u2297y, where the entries of y "
            "are a_1/%d, a_2/%d, ..., a_d/%d with positive integers a_i summing to %d. "
            "Answer with the minimum integer d, or the single word none if no dimension "
            "d works."
            % (n, w, x, D, n, D, fixed, D, D, D, D)
        )
