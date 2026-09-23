import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'heap_splitting_nimber_recursion (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_non_local_structured_r4/heap_splitting_nimber_recursion',
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


def _xor(seq):
    out = 0
    for v in seq:
        out ^= v
    return out


class _NimberSolver:
    def __init__(self, move_lists):
        self.mls = move_lists
        self._cache = {}

    def nimber(self, n):
        if n in self._cache:
            return self._cache[n]
        if n == 0:
            return 0
        reachable = set()
        for splits in self.mls[n]:
            reachable.add(_xor(self.nimber(s) for s in splits))
        g = 0
        while g in reachable:
            g += 1
        self._cache[n] = g
        return g


@dataclass
class HeapSplitConfig(Config):
    max_heap: int = 12
    split_prob: float = 0.55

    def apply_difficulty(self, level):
        self.max_heap = min(16, 10 + 2 * level)
        self.split_prob = min(0.85, 0.45 + 0.07 * level)


def _build_move_lists(max_heap, rng):
    move_lists = [[] for _ in range(max_heap + 1)]
    for n in range(2, max_heap + 1):
        splits_set = set()
        for take in range(1, n):
            splits_set.add((n - take,))
        if n >= 3:
            k = rng.randint(2, min(3, n - 1))
            splits_set.add(tuple(sorted(rng.sample(range(1, n), k))))
        move_lists[n] = sorted(splits_set)
    return move_lists


class HeapSplitNimber(Task):
    summary = "Evaluate take-away games whose moves remove tokens and split the heap into independent subheaps whose values combine by XOR; answers give a heap's nimber, the mex-derived value table up to n, or a winning opening move."
    design_choice = "Answer as the nimber of the initial heap, with heap sizes up to 20 and move sets that force recursive mex computation across many splits."
    config_cls = HeapSplitConfig
    task_version = 2

    def generate_entry(self):
        max_heap = self.config.max_heap
        rng = random
        move_lists = _build_move_lists(max_heap, rng)
        solver = _NimberSolver(move_lists)
        heap = rng.randint(6, max_heap)
        gold = solver.nimber(heap)
        assert 0 <= gold <= 10 ** 6
        instance = {
            "heap": heap,
            "max_heap": max_heap,
            "moves": [list(m) for m in move_lists[1:]],
        }
        return Entry(metadata={"instance": instance, "max_heap": max_heap}, answer=str(gold))

    def render_prompt(self, metadata):
        inst = metadata["instance"]
        heap = inst["heap"]
        lines = []
        for n, moves in enumerate(inst["moves"], start=1):
            parts = []
            for splits in moves:
                if len(splits) == 1:
                    parts.append(f"remove {n - splits[0]} token(s)")
                else:
                    parts.append("split into " + "+".join(str(s) for s in splits))
            lines.append(f"of size {n}: " + "; ".join(parts))
        body = "\n".join(lines)
        return (
            "A take-away game is played on a single heap of tokens. From a heap of size n, "
            "a move either removes some tokens leaving one smaller heap, or (for some sizes) "
            "splits n into several independent subheaps which are then played separately. "
            "The game value (Grundy nimber) of a heap is the mex of the XOR-combined values "
            "of the heaps reachable in one move; the positions are lost exactly when the "
            f"nimber is 0. Move sets:\n{body}\n"
            f"What is the nimber of a heap of size {heap}? Answer with a single non-negative integer."
        )

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(float(answer)) == int(entry.answer) else 0.0
        except (TypeError, ValueError):
            return 0.0
