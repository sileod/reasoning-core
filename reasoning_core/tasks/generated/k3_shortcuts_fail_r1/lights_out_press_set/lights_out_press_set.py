import random
from dataclasses import dataclass

import numpy as np

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'lights_out_press_set (draw 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/lights_out_press_set',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


def _toggle_matrix(rows, cols):
    n = rows * cols
    mat = np.zeros((n, n), dtype=np.int8)
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            mat[i, i] = 1
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    mat[i, nr * cols + nc] = 1
    return mat


def _rref(mat, rhs):
    a = mat.astype(np.int8).copy()
    b = np.asarray(rhs, dtype=np.int8).reshape(-1).copy()
    rows, cols = a.shape
    r = 0
    pivots = []
    for c in range(cols):
        pivot = None
        for rr in range(r, rows):
            if a[rr, c]:
                pivot = rr
                break
        if pivot is None:
            continue
        if pivot != r:
            a[[r, pivot]] = a[[pivot, r]]
            b[r], b[pivot] = b[pivot], b[r]
        for rr in range(rows):
            if rr != r and a[rr, c]:
                a[rr] ^= a[r]
                b[rr] ^= b[r]
        pivots.append(c)
        r += 1
        if r == rows:
            break
    ranka = len(pivots)
    aug = np.hstack([a, b.reshape(-1, 1)])
    rankaug = np.linalg.matrix_rank(aug % 2)
    return pivots, ranka, rankaug, a, b, cols


def _is_consistent(mat, rhs):
    _, ranka, rankaug, _, _, _ = _rref(mat, rhs)
    return ranka == rankaug


def _unique_solve(mat, rhs):
    pivots, ranka, rankaug, a, b, cols = _rref(mat, rhs)
    if ranka != rankaug:
        return None
    x = [0] * cols
    for idx, pc in enumerate(pivots):
        x[pc] = int(b[idx] % 2)
    return x


def _find_conflicting_cell(rows, cols, sol):
    mat = _toggle_matrix(rows, cols)
    n = rows * cols
    lit = mat @ np.asarray(sol, dtype=np.int8) % 2
    return lit.reshape(rows, cols)


@dataclass
class LightsOutPressSetV2Config(Config):
    max_side: int = 4
    solvable_p: float = 0.5

    def apply_difficulty(self, level):
        self.max_side = min(3 + level, 8)
        self.solvable_p = 0.5


def _parse_answer(text, n_cells):
    if isinstance(text, str):
        s = text.strip()
    else:
        s = str(text).strip()
    if s == "":
        return None
    if s.upper() == "NONE":
        return frozenset()
    try:
        parts = [int(t) for t in s.split()]
    except ValueError:
        return None
    if not parts:
        return frozenset()
    if any(p < 0 or p >= n_cells for p in parts):
        return None
    return frozenset(parts)


class LightsOutPressSet(Task):
    summary = ("Find which cells to press on a toggle grid where each press flips itself and "
               "its neighbors so the given pattern goes dark, planning rows over parity rather "
               "than chasing lit cells; answer is the sorted press list or NONE.")
    design_choice = ("Vary grid dimensions from small to large and include guaranteed-solvable "
                     "and unsolvable patterns by controlling the linear system's rank; answer is "
                     "the unique sorted press list or NONE.")
    config_cls = LightsOutPressSetV2Config

    def generate_entry(self):
        cfg = self.config
        attempts = 0
        while attempts < 200:
            attempts += 1
            rows = random.randint(3, cfg.max_side)
            cols = random.randint(3, cfg.max_side)
            n = rows * cols
            mat = _toggle_matrix(rows, cols)
            ranka = np.linalg.matrix_rank(mat % 2)

            want_solvable = random.random() < cfg.solvable_p

            if want_solvable:
                if ranka != n:
                    continue
                for _ in range(20):
                    press = [random.randint(0, 1) for _ in range(n)]
                    if not any(press):
                        continue
                    lit = (mat % 2) @ np.asarray(press, dtype=np.int8) % 2
                    sol = _unique_solve(mat, lit)
                    if sol is not None and sol == press:
                        break
                else:
                    continue
                pattern = lit.reshape(rows, cols).astype(int)
                cell_list = sorted(i for i, v in enumerate(sol) if v)
                answer = " ".join(str(i) for i in cell_list)
                self._check_gold(rows, cols, pattern, cell_list, None)
                return self._build_entry(rows, cols, pattern, answer, cell_list, True)
            else:
                if ranka == n:
                    continue
                for _ in range(50):
                    lit = [random.randint(0, 1) for _ in range(n)]
                    if not _is_consistent(mat, lit):
                        break
                else:
                    continue
                pattern = np.asarray(lit, dtype=np.int8).reshape(rows, cols).astype(int)
                answer = "NONE"
                self._check_gold(rows, cols, pattern, None, lit)
                return self._build_entry(rows, cols, pattern, answer, None, False)
        raise RuntimeError("LightsOutPressSet: failed to construct a valid instance")

    def _check_gold(self, rows, cols, pattern, cell_list, lit):
        n = rows * cols
        mat = _toggle_matrix(rows, cols)
        flat = np.asarray(pattern, dtype=np.int8).reshape(-1)
        if cell_list is None:
            assert not _is_consistent(mat, flat), "unsolvable instance solved unexpectedly"
        else:
            indicator = np.zeros(n, dtype=np.int8)
            indicator[list(cell_list)] = 1
            assert np.array_equal((mat % 2) @ indicator % 2, flat), \
                "press set does not reproduce the pattern"

    def _build_entry(self, rows, cols, pattern, answer, cell_list, solvable):
        flat_pattern = pattern.reshape(-1).tolist()
        n = rows * cols
        metadata = {
            "rows": rows,
            "cols": cols,
            "grid": [pattern[r, :].tolist() for r in range(rows)],
            "flat_pattern": flat_pattern,
            "solvable": solvable,
            "press": None if cell_list is None else list(cell_list),
            "n_cells": n,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        rows = metadata["rows"]
        cols = metadata["cols"]
        grid = metadata["grid"]
        lines = []
        for r in range(rows):
            lines.append(" ".join(str(int(grid[r][c])) for c in range(cols)))
        grid_txt = "\n".join(lines)
        return (
            f"Cells are numbered 0..{rows * cols - 1} in row-major order: the cell at row r, "
            f"column c has index r*{cols}+c. A 1 means the cell is lit and a 0 means dark. "
            f"Pressing a cell toggles it and every orthogonally adjacent cell (up, down, left, "
            f"right, when present). Each cell may be pressed at most once.\n"
            f"Grid ({rows} rows, {cols} cols):\n{grid_txt}\n"
            f"Give the set of cells to press (sorted ascending, space-separated indices) so that "
            f"every cell ends dark, or the exact word NONE if no such set exists. The pattern of "
            f"1s is guaranteed to have a unique answer if pressable; it is NONE exactly when no "
            f"set of presses can darken every lit cell.\nAnswer:"
        )

    def score_answer(self, answer, entry):
        n_cells = entry.metadata["n_cells"]
        gold_flat = frozenset(entry.metadata.get("press") or [])
        parsed = _parse_answer(answer, n_cells)
        if parsed is None:
            return 0.0
        if not gold_flat:
            return 1.0 if parsed == frozenset() else 0.0
        if not parsed:
            return 0.0
        return 1.0 if parsed == gold_flat else 0.0
