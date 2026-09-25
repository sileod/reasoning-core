import math
import random
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _gen_partition(m):
    length = random.randint(max(2, m - 2), m + 2)
    prev = m + random.randint(0, 4)
    seq = []
    for _ in range(length):
        if prev < 1:
            break
        v = random.randint(max(1, prev - 4), prev)
        seq.append(v)
        prev = v - 1
    seq = sorted(seq, reverse=True)
    while seq and seq[-1] == 0:
        seq.pop()
    return seq


def _rim_strips(part, size):
    rows = len(part)
    present = set()
    for r, ln in enumerate(part):
        for c in range(ln):
            present.add((r, c))
    rim = []
    for (r, c) in present:
        if ((r + 1, c) not in present) or ((r, c + 1) not in present):
            rim.append((r, c))
    results = []
    for combo in combinations(rim, size):
        remove = set(combo)
        bad = False
        for (r, c) in remove:
            if (r, c + 1) in remove and (r + 1, c) in remove and (r + 1, c + 1) in remove:
                bad = True
                break
        if bad:
            continue
        if not _connected(remove):
            continue
        new_part = _to_partition(remove, present, rows)
        if new_part is None:
            continue
        height = 1 + max(r for (r, c) in remove) - min(r for (r, c) in remove)
        results.append((new_part, height))
    return results


def _connected(cells):
    if not cells:
        return False
    start = next(iter(cells))
    seen = {start}
    stack = [start]
    while stack:
        r, c = stack.pop()
        for nb in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if nb in cells and nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return len(seen) == len(cells)


def _to_partition(remove, present, rows):
    remain = present - remove
    colcnt = []
    for r in range(rows):
        colcnt.append(sum(1 for (rr, c) in remain if rr == r))
    for a, b in zip(colcnt, colcnt[1:]):
        if a < b:
            return None
    return colcnt


def signed_total(part, sizes):
    def rec(p, idx):
        if idx == len(sizes):
            return Fraction(1, 1)
        total = Fraction(0, 1)
        for new_p, h in _rim_strips(p, sizes[idx]):
            sign = -1 if (h - 1) % 2 else 1
            total += Fraction(sign, h) * rec(new_p, idx + 1)
        return total

    return rec(list(part), 0)


def format_fraction(frac):
    num = int(frac.numerator)
    den = int(frac.denominator)
    g = math.gcd(abs(num), abs(den))
    num //= g
    den //= g
    if den < 0:
        num = -num
        den = -den
    return f"{num}/{den}"


TASK_META = {'parent_source_id': None,
 'idea': 'partition_rim_strip_cancellation (variant 2 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_specific_r4/partition_rim_strip_cancellation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 241712510,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class PartitionRimStripCancellationV2Config(Config):
    m: int = 4
    k: int = 2
    smax: int = 2

    def apply_difficulty(self, level):
        self.m = 4 + level
        self.k = 2 + level // 3
        self.smax = min(2 + level // 2, 4)


class PartitionRimStripCancellation(Task):
    summary = ("Count complete histories that remove connected no-2x2 rim strips from partitions "
               "along a specified size sequence, weight each strip by parity sign (-1)^(h-1)/h, "
               "sum over histories, and return the signed total as a reduced fraction num/den.")
    design_choice = ("Answers are reduced fractions, where the total is expressed as a rational "
                     "number with denominator equal to the product of all strip heights in the "
                     "sequence.")
    config_cls = PartitionRimStripCancellationV2Config

    def generate_entry(self):
        for _ in range(300):
            part = _gen_partition(self.config.m)
            total = sum(part)
            if total < 2:
                continue
            smax = min(self.config.smax, total)
            if smax < 1:
                continue
            sizes = [random.randint(1, smax) for _ in range(self.config.k)]
            frac = signed_total(part, sizes)
            num = int(frac.numerator)
            if num == 0:
                continue
            answer = format_fraction(frac)
            if answer == "0/1":
                continue
            return Entry(metadata={"partition": part, "sizes": sizes},
                         answer=answer)
        raise RuntimeError("failed to generate a non-trivial instance")

    def render_prompt(self, metadata):
        part = " ".join(str(x) for x in metadata["partition"])
        sizes = " ".join(str(x) for x in metadata["sizes"])
        return (
            f"Start from the partition lambda = {part} (rows of boxes, top row first). You will "
            f"remove rim strips one at a time from its Young diagram. A rim strip is a connected "
            f"set of boxes on the boundary of the current diagram that contains no 2x2 block, and "
            f"removing it must leave a partition. You must remove strips whose box counts match the "
            f"given sizes in order: sizes = {sizes}. In each complete removal history you use up "
            f"exactly all the given sizes in order, and a branch that cannot remove a strip of the "
            f"current required size contributes nothing. Every time you remove a strip of height h "
            f"(the number of distinct rows it spans) it contributes a factor (-1)^(h-1)/h. The "
            f"signed total is the sum, over all complete removal histories, of the products of the "
            f"per-strip factors. Report the signed total as a single reduced fraction a/b with "
            f"b > 0, writing integers with denominator 1, e.g. 3/1, -5/2 or 1/2. Give only the "
            f"reduced fraction as your answer."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            got = Fraction(answer)
        except Exception:
            return 0.0
        gold = Fraction(entry.answer)
        return 1.0 if got == gold else 0.0
