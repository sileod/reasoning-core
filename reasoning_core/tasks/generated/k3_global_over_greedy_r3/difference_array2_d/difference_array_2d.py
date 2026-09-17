import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'difference_array_2d (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_over_greedy_r3/difference_array_2d',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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


def _parse_rectangles(text, rows, cols):
    """Parse 'r1 c1 r2 c2 delta' per line into tuples; None on any malformation."""
    if not isinstance(text, str):
        return None
    rects = []
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line:
            return None
        parts = line.split()
        if len(parts) != 5:
            return None
        try:
            r1, c1, r2, c2, delta = (int(p) for p in parts)
        except ValueError:
            return None
        if not (0 <= r1 < r2 < rows and 0 <= c1 < c2 < cols):
            return None
        rects.append((r1, c1, r2, c2, delta))
    return rects


def _apply_rectangles(rows, cols, rects):
    """Reference 2D difference array: mark corners, prefix-sum rows, then columns."""
    diff = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r1, c1, r2, c2, delta in rects:
        diff[r1][c1] += delta
        diff[r1][c2] -= delta
        diff[r2][c1] -= delta
        diff[r2][c2] += delta
    row = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        acc = 0
        for c in range(cols):
            acc += diff[r][c]
            row[r][c] = acc
    grid = [[0] * cols for _ in range(rows)]
    for c in range(cols):
        acc = 0
        for r in range(rows):
            acc += row[r][c]
            grid[r][c] = acc
    return grid


def _apply_rectangle_naive(rows, cols, rects):
    grid = [[0] * cols for _ in range(rows)]
    for r1, c1, r2, c2, delta in rects:
        for r in range(r1, r2):
            for c in range(c1, c2):
                grid[r][c] += delta
    return grid


def _format_grid(grid):
    return "; ".join(" ".join(str(v) for v in row) for row in grid)


def _parse_grid(text):
    if not isinstance(text, str):
        return None
    text = text.strip().strip("|")
    try:
        return [[int(tok) for tok in row.split()] for row in text.split(";")]
    except ValueError:
        return None


@dataclass
class DifferenceArray2DConfig(Config):
    rows: int = 4
    cols: int = 5
    n_rects: int = 3
    max_delta: int = 3

    def apply_difficulty(self, level):
        self.rows = 4 + 2 * level
        self.cols = 5 + 3 * level
        self.n_rects = 3 + 3 * level
        self.max_delta = 3 + level


class DifferenceArray2D(Task):
    summary = ("Given a 2D grid and rectangle updates or queries, apply the 2D difference "
               "array technique and output final cell values or query results; operations "
               "mix range adds and point reads. This variant always asks for the full "
               "final grid, given as a canonical row-major integer list after all "
               "rectangle adds are applied, with no queries.")
    design_choice = ("Answers are the full final grid as a canonical row-major integer "
                     "list after all rectangle adds are applied, with no queries.")
    config_cls = DifferenceArray2DConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(200):
            rows, cols = cfg.rows, cfg.cols
            rects = []
            for _ in range(cfg.n_rects):
                r1 = random.randrange(rows - 1)
                c1 = random.randrange(cols - 1)
                r2 = random.randrange(r1 + 1, rows)
                c2 = random.randrange(c1 + 1, cols)
                delta = random.randint(-cfg.max_delta, cfg.max_delta)
                rects.append((r1, c1, r2, c2, delta))
            grid = _apply_rectangle_naive(rows, cols, rects)
            if all(v == 0 for row in grid for v in row):
                continue
            witness = _apply_rectangles(rows, cols, rects)
            if witness != grid:
                raise RuntimeError(
                    "difference_array_2d: difference-array reconstruction disagrees "
                    "with the naive rectangle addition")
            if len(rects) > 1 and rects[:-1] == rects[1:]:
                continue
            answer = _format_grid(grid)
            metadata = {
                "rows": int(rows),
                "cols": int(cols),
                "rectangles": [[int(v) for v in rect] for rect in rects],
                "grid": [[int(v) for v in row] for row in grid],
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("difference_array_2d: failed to produce a valid instance")

    def render_prompt(self, metadata):
        rows, cols = metadata["rows"], metadata["cols"]
        rect_lines = "\n".join(
            f"{r1} {c1} {r2} {c2} {d}"
            for r1, c1, r2, c2, d in metadata["rectangles"]
        )
        return (
            f"A {rows}x{cols} grid of integers starts as all zeros. Each update is a "
            f"rectangle 'r1 c1 r2 c2 delta' using half-open index ranges: it adds delta "
            f"to every cell with r1 <= row < r2 and c1 <= col < c2 (0-based, so "
            f"'0 1 2 3 -4' means add -4 to rows 0-1 and columns 1-2 and '2 3' in the "
            f"pair is an exclusive upper bound). Apply all of these updates:\n"
            f"{rect_lines}\n\n"
            f"Report the entire final grid, all cells, as {rows} rows separated by "
            f"semicolons, each row listing its {cols} integers space-separated, in "
            f"row-major order from cell (0,0). Example for a 2x2 grid: 3 -1; 0 5"
        )

    def score_answer(self, answer, entry):
        got = _parse_grid(answer)
        ref = _parse_grid(entry.answer)
        if got is None or ref is None:
            return 0.0
        return 1.0 if got == ref else 0.0

    def distractor_candidates(self, entry):
        md = entry.metadata
        rows, cols = md["rows"], md["cols"]
        rects = [tuple(r) for r in md["rectangles"]]
        variants = []
        if rects:
            variants.append(_apply_rectangle_naive(rows, cols, rects[:-1]))
            first = list(rects[0])
            first[-1] = -first[-1]
            variants.append(_apply_rectangle_naive(rows, cols, [tuple(first)] + rects[1:]))
            swapped = [rects[-1][:2] + rects[-1][2:4][::-1] + (rects[-1][4],)]
            variants.append(_apply_rectangle_naive(rows, cols, rects[:-1] + swapped))
            variants.append([[v + 1 for v in row] for row in md["grid"]])
            variants.append([list(row) for row in md["grid"]][::-1])
        return [_format_grid(v) for v in variants if v != md["grid"]]
