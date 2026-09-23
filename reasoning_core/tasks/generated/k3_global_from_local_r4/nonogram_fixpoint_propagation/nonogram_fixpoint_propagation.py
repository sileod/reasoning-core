import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class NonogramConfig(Config):
    size: int = 5
    fill_density: float = 0.55

    def apply_difficulty(self, level):
        self.size = int(round(4 + level * 1.5))
        self.fill_density = 0.45 + 0.05 * min(level, 5)


def _runs(bits):
    out = []
    i = 0
    n = len(bits)
    while i < n:
        if bits[i]:
            j = i
            while j < n and bits[j]:
                j += 1
            out.append(j - i)
            i = j
        else:
            i += 1
    return out


def _line_clues(cells):
    runs = _runs(cells)
    if not runs:
        return (0,)
    return tuple(runs)


def _possible_fills(clue, length):
    if clue == (0,):
        yield tuple([False] * length)
        return
    k = len(clue)
    init = [False] * length
    res = []

    def rec(i, arr, start):
        if i == k:
            res.append(tuple(arr))
            return
        seg_len = clue[i]
        tail_min = sum(clue[i + 1:]) + (k - 1 - i)
        last_start = length - tail_min - seg_len
        for s in range(start, last_start + 1):
            if any(arr[s:s + seg_len]):
                continue
            new = list(arr)
            for o in range(seg_len):
                new[s + o] = True
            rec(i + 1, new, s + seg_len + 1 if i < k - 1 else s + seg_len)

    rec(0, init, 0)
    for r in res:
        yield r


def _position_force(clue, length):
    fills = list(_possible_fills(clue, length))
    if not fills:
        return set()
    return {i for i in range(length) if all(f[i] for f in fills)}


def _pos_force_with_fixed(clue, length, fixed_true, fixed_false):
    fills = [f for f in _possible_fills(clue, length)
             if all(f[i] for i in fixed_true) and all(not f[i] for i in fixed_false)]
    if not fills:
        return None
    return {i for i in range(length) if all(f[i] for f in fills)}


def _white_forced(clue, length, fixed_true, fixed_false):
    fills = [f for f in _possible_fills(clue, length)
             if all(f[i] for i in fixed_true) and all(not f[i] for i in fixed_false)]
    if not fills:
        return set()
    return {i for i in range(length) if not any(f[i] for f in fills)}


def _fixpoint(size, row_clues, col_clues):
    cell = [[None] * size for _ in range(size)]
    for r in range(size):
        for i in _pos_force_with_fixed(row_clues[r], size, set(), set()):
            cell[r][i] = 'B'
        for i in _white_forced(row_clues[r], size, set(), set()):
            cell[r][i] = 'W'
    for c in range(size):
        for i in _pos_force_with_fixed(col_clues[c], size, set(), set()):
            cell[i][c] = 'B'
        for i in _white_forced(col_clues[c], size, set(), set()):
            cell[i][c] = 'W'
    while True:
        changed = False
        for r in range(size):
            ft = {c for c in range(size) if cell[r][c] == 'B'}
            ff = {c for c in range(size) if cell[r][c] == 'W'}
            for i in _pos_force_with_fixed(row_clues[r], size, ft, ff):
                if cell[r][i] is None:
                    cell[r][i] = 'B'
                    changed = True
            for i in _white_forced(row_clues[r], size, ft, ff):
                if cell[r][i] is None:
                    cell[r][i] = 'W'
                    changed = True
        for c in range(size):
            ft = {r for r in range(size) if cell[r][c] == 'B'}
            ff = {r for r in range(size) if cell[r][c] == 'W'}
            for i in _pos_force_with_fixed(col_clues[c], size, ft, ff):
                if cell[i][c] is None:
                    cell[i][c] = 'B'
                    changed = True
            for i in _white_forced(col_clues[c], size, ft, ff):
                if cell[i][c] is None:
                    cell[i][c] = 'W'
                    changed = True
        if not changed:
            break
    return cell


class NonogramFixpointPropagation(Task):
    summary = "Nonograms with row and column clues: force cells per line from clue overlap, propagate fixed cells across crossing lines to a fixpoint; answer a queried cell (B/W/?) after propagation."
    design_choice = "Queried cell answer: return a single canonical token ('B'/'W'/'?') for a specified coordinate after full fixpoint propagation."
    config_cls = NonogramConfig

    def generate_entry(self):
        size = self.config.size
        grid = []
        for _ in range(size):
            row = [random.random() < self.config.fill_density for _ in range(size)]
            grid.append(row)
        row_clues = [_line_clues(g) for g in grid]
        col_clues = [_line_clues([grid[r][c] for r in range(size)]) for c in range(size)]

        cell = _fixpoint(size, row_clues, col_clues)

        r = random.randrange(size)
        c = random.randrange(size)
        st = cell[r][c]
        answer = st if st is not None else '?'
        metadata = {
            'size': size,
            'row_clues': [list(x) for x in row_clues],
            'col_clues': [list(x) for x in col_clues],
            'grid': [[int(bool(b)) for b in row] for row in grid],
            'query': {'type': 'cell', 'r': r, 'c': c},
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        size = metadata['size']
        r, c = metadata['query']['r'], metadata['query']['c']
        return (
            f"Consider a {size}x{size} nonogram grid. Row i (0-indexed) has clues "
            f"{metadata['row_clues']} and column j has clues {metadata['col_clues']}. "
            f"After performing full fixpoint propagation (repeatedly marking cells forced by "
            f"each line's clue overlap, propagating those marks across crossing lines until no "
            f"further cell is forced), what is the final known state of the cell at row {r}, "
            f"column {c}? Answer with exactly one of B (black/filled), W (white/empty), or "
            f"? (still unknown)."
        )

    def score_answer(self, answer, entry):
        size = entry['metadata']['size']
        row_clues = [tuple(x) for x in entry['metadata']['row_clues']]
        col_clues = [tuple(x) for x in entry['metadata']['col_clues']]
        r, c = entry['metadata']['query']['r'], entry['metadata']['query']['c']
        cell = _fixpoint(size, row_clues, col_clues)
        st = cell[r][c]
        exp = st if st is not None else '?'
        return 1.0 if answer.strip() == exp else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'nonogram_fixpoint_propagation (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/nonogram_fixpoint_propagation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
