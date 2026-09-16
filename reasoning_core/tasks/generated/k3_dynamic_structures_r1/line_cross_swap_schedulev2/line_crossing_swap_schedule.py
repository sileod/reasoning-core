import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'line_crossing_swap_schedule (draw 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dynamic_structures_r1/line_crossing_swap_schedule',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class LineCrossingSwapScheduleConfig(Config):
    n_lines: int = 5
    max_abs_a: int = 5
    max_abs_b: int = 8

    def apply_difficulty(self, level):
        self.n_lines = stochastic_rounding(4 + level)
        self.max_abs_a = 3 + level
        self.max_abs_b = 5 + 2 * level


def _crossing_time(l1, l2):
    a1, b1 = l1[0], l1[1]
    a2, b2 = l2[0], l2[1]
    da = a1 - a2
    db = b1 - b2
    if da == 0:
        return None
    return Fraction(-db, da)


def _verify_permutation(lines, perm):
    seen = set()
    for i in perm:
        if i in seen:
            return False
        seen.add(i)
    if len(seen) != len(lines):
        return False
    return sorted(perm) == [i for i in range(len(lines))]


class LineCrossSwapSchedulev2(Task):
    summary = "Given lines y=at+b with integer coefficients, replay all pairwise crossings as adjacent swaps in the current ordering ordered by exact rational time with simultaneous crossings swapped concurrently in index order, and report the resulting final permutation of line indices."
    config_cls = LineCrossingSwapScheduleConfig
    design_choice = "Ask for the final permutation only, encoded as a space-separated list of line indices after replaying all simultaneous crossings in a fixed tie-break order."
    task_version = 2

    def _lines(self):
        n = self.config.n_lines
        lines = []
        used = set()
        while len(lines) < n:
            a = random.randint(-self.config.max_abs_a, self.config.max_abs_a)
            b = random.randint(-self.config.max_abs_b, self.config.max_abs_b)
            key = int(a) * 1000 + int(b)
            if key in used:
                continue
            used.add(key)
            lines.append((int(a), int(b)))
        return lines

    def _replay(self, lines):
        events = []
        for p in range(len(lines)):
            for q in range(p + 1, len(lines)):
                t = _crossing_time(lines[p], lines[q])
                if t is not None:
                    events.append((t, p, q))
        events.sort(key=lambda e: (e[0], e[1], e[2]))
        order = list(range(len(lines)))
        idx = 0
        while idx < len(events):
            t = events[idx][0]
            group_swaps = []
            while idx < len(events) and events[idx][0] == t:
                group_swaps.append((events[idx][1], events[idx][2]))
                idx += 1
            group_swaps.sort(key=lambda s: (s[0], s[1]))
            pos = {i: order.index(i) for i in order}
            to_swap = []
            swapped_positions = set()
            for (ia, ib) in group_swaps:
                pa, pb = pos[ia], pos[ib]
                pmin, pmax = min(pa, pb), max(pa, pb)
                if pmax - pmin == 1 and pmin not in swapped_positions and pmax not in swapped_positions:
                    to_swap.append((pmin, pmax, ia, ib))
                    swapped_positions.add(pmin)
                    swapped_positions.add(pmax)
            for (pmin, pmax, ia, ib) in to_swap:
                order[pmin], order[pmax] = order[pmax], order[pmin]
        return order

    def generate_entry(self):
        while True:
            lines = self._lines()
            order = self._replay(lines)
            if len(order) != len(lines):
                continue
            if all(i == order[i] for i in range(len(order))):
                continue
            if not _verify_permutation(lines, order):
                continue
            metadata = {
                "lines": [(int(a), int(b)) for (a, b) in lines],
                "final_permutation": order,
            }
            answer = " ".join(str(i) for i in order)
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = metadata["lines"]
        desc = "; ".join(f"line {i}: y={a}t+{b}" for i, (a, b) in enumerate(lines))
        return (
            f"You have lines with these y values as functions of time t: {desc}. "
            f"Start with the lines ordered 0, 1, 2, ... initially. Whenever two lines cross, "
            "swap them in the ordering if they are adjacent at that moment. Process all "
            "crossings sorted by their exact rational time in increasing order; when several "
            "crossings happen at the same time, swap all adjacent pairs simultaneously. "
            "Report the final ordering as a space-separated list of line indices."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            parts = [int(x) for x in answer.strip().split()]
        except ValueError:
            return 0.0
        expected = list(entry.metadata["final_permutation"])
        if len(parts) != len(expected):
            return 0.0
        return 1.0 if parts == expected else 0.0
