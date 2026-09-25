import random
import itertools
from dataclasses import dataclass, field
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

_ENTRIES = [Fraction(0), Fraction(1, 3), Fraction(2, 3), Fraction(1)]


def _valid_rows():
    rows = set()
    for combo in itertools.combinations_with_replacement(_ENTRIES, 3):
        if sum(combo) == 1:
            for p in itertools.permutations(combo):
                rows.add(p)
    return sorted(rows)


_ROW_TYPES = _valid_rows()


def _det3(A):
    a, b, c = A[0]
    d, e, f = A[1]
    g, h, i = A[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _inverse(A):
    a, b, c, d, e, f, g, h, i = A[0] + A[1] + A[2]
    det = _det3(A)
    return [
        [(e * i - f * h) / det, -(b * i - c * h) / det, (b * f - c * e) / det],
        [-(d * i - f * g) / det, (a * i - c * g) / det, -(a * f - c * d) / det],
        [(d * h - e * g) / det, -(a * h - b * g) / det, (a * e - b * d) / det],
    ]


def _feasible_garbling(A, B):
    det = _det3(A)
    if det == 0:
        return None
    inv = _inverse(A)
    G = [
        [sum(inv[r][j] * B[j][k] for j in range(3)) for k in range(3)]
        for r in range(3)
    ]
    ok = all(e >= 0 for row in G for e in row)
    return ok


def _matmul(A, G):
    return [
        [sum(A[i][j] * G[j][k] for j in range(3)) for k in range(3)]
        for i in range(3)
    ]


def _fmt(M):
    def s(x):
        if x.denominator == 1:
            return str(x.numerator)
        return f"{x.numerator}/{x.denominator}"

    return "[" + "; ".join("[" + ", ".join(s(c) for c in row) + "]" for row in M) + "]"


def _rand_channel(mixed_p, rng):
    deterministic = [r for r in _ROW_TYPES if Fraction(1) in r]
    mixed = [r for r in _ROW_TYPES if Fraction(1) not in r]
    return [list(rng.choice(mixed if rng.random() < mixed_p else deterministic)) for _ in range(3)]


def _unit_garbling(rng):
    G = [[Fraction(0)] * 3 for _ in range(3)]
    for r in range(3):
        G[r][rng.randrange(3)] = Fraction(1)
    return G


@dataclass
class GarblingConfig(Config):
    level: int = 0
    construct_prob: float = 0.5
    mixed_p: float = 0.35

    def apply_difficulty(self, level):
        self.mixed_p = min(0.95, 0.35 + 0.10 * level)
        self.construct_prob = max(0.25, 0.50 - 0.05 * level)


def _canonical(M):
    return tuple(tuple(int(c.numerator * 3 / c.denominator) for c in row) for row in M)


class ExperimentGarblingOrder(Task):
    summary = "Compare 3x3 rational channels by whether state-independent randomization garbles A into B, deciding feasibility, equivalence, and incomparability: answer yes/no."
    design_choice = "Use 3x3 rational channel tables with entries from {0, 1/3, 2/3, 1}, and ask whether A can be garbled to B via a stochastic matrix with rational entries, with answer 'yes' or 'no'."
    config_cls = GarblingConfig

    def generate_entry(self):
        A = _rand_channel(self.config.mixed_p, random)
        while _det3(A) == 0:
            A = _rand_channel(self.config.mixed_p, random)

        if random.random() < self.config.construct_prob:
            G = _unit_garbling(random)
            B = _matmul(A, G)
            label = True
        else:
            B = _rand_channel(self.config.mixed_p, random)
            label = _feasible_garbling(A, B)

        assert label is not None
        assert label == (_feasible_garbling(A, B) is True)
        assert _det3(A) != 0
        assert all(sum(r) == 1 for r in A) and all(sum(r) == 1 for r in B)
        assert all(c in _ENTRIES for row in A for c in row)
        assert all(c in _ENTRIES for row in B for c in row)

        metadata = {
            "A": _canonical(A),
            "B": _canonical(B),
            "A_str": _fmt(A),
            "B_str": _fmt(B),
        }
        return Entry(metadata=metadata, answer="yes" if label else "no")

    def render_prompt(self, metadata):
        a = metadata["A_str"]
        b = metadata["B_str"]
        return (
            "We compare two finite observation channels. A channel is a "
            "row-stochastic matrix (each row sums to 1). We say channel A can be "
            "garbled to channel B (A more capable than B in the Blackwell sense) "
            "when there exists a stochastic matrix G (rows sum to 1, entries "
            "non-negative reals) with B = A G.\n"
            f"Channel A = {a}.\n"
            f"Channel B = {b}.\n"
            "Can A be garbled to B? Judge whether such a garbling exists and "
            "write your conclusion as one word, yes or no, in the box labeled "
            "verdict."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'experiment_garbling_order (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_representation_r4/experiment_garbling_order',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
