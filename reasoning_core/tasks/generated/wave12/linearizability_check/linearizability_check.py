import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class LinearizabilityCheckConfig(Config):
    n_ops: int = 3
    max_val: int = 3

    def apply_difficulty(self, level):
        self.n_ops = 2 * level + 3
        self.max_val = 2 * level + 2


_UNDEF = -1


def _is_linearizable(history, intervals):
    """Backtracking linearization search for a read/write register history.

    Real-time order (i before j when interval i ends before interval j starts)
    plus a sequential register spec (read returns most recent preceding write).
    Returns True if some sequential order satisfies both. Linearizable register
    recognition is polynomial; this memoized search is fast for the small sizes
    generated (n <= 13).
    """
    n = len(history)
    pred_mask = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if intervals[i][1] <= intervals[j][0]:
                pred_mask[j] |= 1 << i
            elif intervals[j][1] <= intervals[i][0]:
                pred_mask[i] |= 1 << j

    memo = {}

    def search(placed_mask, value):
        if placed_mask == (1 << n) - 1:
            return True
        key = (placed_mask, value)
        if key in memo:
            return memo[key]
        for i in range(n):
            if placed_mask >> i & 1:
                continue
            if pred_mask[i] & ~placed_mask:
                continue
            op, v = history[i]
            if op == "read" and value is _UNDEF:
                continue
            nv = v if op == "write" else value
            if search(placed_mask | (1 << i), nv):
                memo[key] = True
                return True
        memo[key] = False
        return False

    return search(0, _UNDEF)


def _render(metadata):
    lines = []
    for idx, ((lo, hi), (op, v)) in enumerate(
        zip(metadata["intervals"], metadata["history"])
    ):
        if op == "write":
            lines.append(f"  op{idx}: write({v}) from {lo} to {hi}")
        else:
            lines.append(f"  op{idx}: read() from {lo} to {hi}")
    return (
        "A shared integer register starts with an undefined value. A history records "
        "time intervals during which each operation overlaps in real time. The "
        "sequential specification: a write(x) sets the register to x; a read() returns "
        "the value written by the most recent preceding write (or is undefined if no "
        "preceding write happens). Operations may overlap in real time; if two "
        "intervals do not overlap, the earlier one finishes before the later one "
        "starts. The history is linearizable if we can order the operations into a "
        "sequence consistent with both the real-time order of non-overlapping "
        "operations and the sequential specification above. Answer 'true' if the "
        "history is linearizable, otherwise 'false'.\n\nHistory:\n"
        + "\n".join(lines)
    )


class LinearizabilityCheck(Task):
    summary = (
        "Given a small concurrent history of register operations (read/write with "
        "overlapping time intervals) and a sequential register specification, answer "
        "whether the history is linearizable. Balanced read/write mixes with "
        "overlapping intervals, boolean true/false answer cut at each level."
    )
    design_choice = "Answer as a canonical boolean string 'true' or 'false', with histories generated to balance both outcomes within each difficulty level."
    config_cls = LinearizabilityCheckConfig

    def generate_entry(self):
        n = self.config.n_ops
        max_val = self.config.max_val
        target = random.choice([True, False])
        for _attempt in range(200):
            history = []
            for _ in range(n):
                if random.random() < 0.5:
                    history.append(("write", random.randint(0, max_val)))
                else:
                    history.append(("read", None))
            points = sorted(random.sample(range(0, 2 * n + 2), 2 * n))
            intervals = [
                (points[2 * i], points[2 * i + 1]) for i in range(n)
            ]
            if _is_linearizable(history, intervals) == target:
                return Entry(
                    metadata={
                        "history": history,
                        "intervals": intervals,
                        "max_val": max_val,
                    },
                    answer="true" if target else "false",
                )
        raise RuntimeError("failed to generate a balanced instance")

    def render_prompt(self, metadata):
        return _render(metadata)


TASK_META = {'parent_source_id': None,
 'idea': 'linearizability_check (draw 1 of 3)',
 'hypothesis': 'external:linearizability_check',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/linearizability_check',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3622015929,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
