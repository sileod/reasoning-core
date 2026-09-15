import random
from dataclasses import dataclass

from reasoning_core.template import Entry, Config, Task, edict

_SE = {
    "cross": {
        "offsets": [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)],
        "word": "a cross (the center cell plus its up, down, left, and right neighbors)",
    },
    "square3": {
        "offsets": [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)],
        "word": "a full 3-by-3 square",
    },
    "vbar": {
        "offsets": [(0, 0), (1, 0), (-1, 0)],
        "word": "a vertical bar (the center cell plus its up and down neighbors)",
    },
    "hbar": {
        "offsets": [(0, 0), (0, 1), (0, -1)],
        "word": "a horizontal bar (the center cell plus its left and right neighbors)",
    },
}

_HM = {
    "corner": {
        "F": [(0, 0), (1, 0), (0, 1)],
        "B": [(1, 1)],
        "word": "a foreground 2-by-2 corner, meaning the cell and its right and down "
                "neighbors are all foreground while the down-right diagonal cell is "
                "background (the other cells do not matter)",
    },
}

_OP_WEIGHTS = [("erode", 3), ("dilate", 3), ("open", 2), ("close", 2), ("hit_miss", 1)]


@dataclass
class BinaryMorphConfig(Config):
    grid_size: int = 4
    n_passes: int = 2
    density: float = 0.5
    max_attempts: int = 200

    def apply_difficulty(self, level):
        self.grid_size = min(10, int(4 + 1.1 * level))
        self.n_passes = min(4, int(2 + 0.5 * level))
        self.density = 0.5


def _erode(grid, se):
    h, w = len(grid), len(grid[0])
    out = []
    for r in range(h):
        row = []
        for c in range(w):
            ok = True
            for dr, dc in se:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w:
                    if not grid[nr][nc]:
                        ok = False
                        break
                else:
                    ok = False
                    break
            row.append(1 if ok else 0)
        out.append(row)
    return out


def _dilate(grid, se):
    h, w = len(grid), len(grid[0])
    out = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            for dr, dc in se:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and grid[nr][nc]:
                    out[r][c] = 1
                    break
    return out


def _openclose(grid, op, se):
    if op == "open":
        return _dilate(_erode(grid, se), se)
    return _erode(_dilate(grid, se), se)


def _hitmiss(grid, pattern):
    h, w = len(grid), len(grid[0])
    F, B = pattern["F"], pattern["B"]
    out = []
    for r in range(h):
        row = []
        for c in range(w):
            ok = True
            for dr, dc in F:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < h and 0 <= nc < w and grid[nr][nc]):
                    ok = False
                    break
            if ok:
                for dr, dc in B:
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < h and 0 <= nc < w and not grid[nr][nc]):
                        ok = False
                        break
            row.append(1 if ok else 0)
        out.append(row)
    return out


_OP_FN = {
    "erode": lambda g, arg: _erode(g, _SE[arg]["offsets"]),
    "dilate": lambda g, arg: _dilate(g, _SE[arg]["offsets"]),
    "open": lambda g, arg: _openclose(g, "open", _SE[arg]["offsets"]),
    "close": lambda g, arg: _openclose(g, "close", _SE[arg]["offsets"]),
    "hit_miss": lambda g, arg: _hitmiss(g, _HM[arg]),
}


def _parse_int(answer):
    try:
        return int(str(answer).strip())
    except (ValueError, TypeError):
        return None


TASK_META = {'parent_source_id': None,
 'idea': 'binary_morphology_passes (draw 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dependence_relevance_r1/binary_morphology_passes',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class BinaryMorphologyPasses(Task):
    summary = ("Compose binary-morphology passes (erode, dilate, open, close, "
               "hit-miss) with chosen structuring elements and zero-fill border "
               "handling over random binary grids; return the count of foreground "
               "cells in the final image.")
    design_choice = ("Answer as a single integer count of foreground cells in the "
                     "final image.")
    task_version = 2
    config_cls = BinaryMorphConfig

    def generate_entry(self):
        cfg = self.config
        for _ in range(cfg.max_attempts):
            h = w = cfg.grid_size
            grid = [[1 if random.random() < cfg.density else 0 for _ in range(w)]
                    for _ in range(h)]
            passes = []
            for _ in range(cfg.n_passes):
                op = random.choices([o for o, _ in _OP_WEIGHTS],
                                    weights=[wt for _, wt in _OP_WEIGHTS])[0]
                if op == "hit_miss":
                    arg = "corner"
                else:
                    arg = random.choice(list(_SE))
                grid = _OP_FN[op](grid, arg)
                passes.append((op, arg))
            count = sum(sum(row) for row in grid)
            if 0 < count < h * w:
                payload = {
                    "grid": ["".join(map(str, r)) for r in grid],
                    "size": [h, w],
                    "passes": passes,
                }
                metadata = edict(
                    grid=[list(r) for r in grid],
                    full_grid=[[c for c in r] for r in grid],
                    h=h, w=w, passes=passes, count=count,
                    payload=payload,
                )
                return Entry(metadata=metadata, answer=str(count))
        raise RuntimeError("Failed to generate a nondegenerate morphology image")

    def render_prompt(self, metadata):
        grid_lines = "\n".join("".join(map(str, r)) for r in metadata.full_grid)
        head = (f"Start with this binary image (0 = background, 1 = foreground), "
                f"{metadata.h} rows by {metadata.w} columns:\n{grid_lines}")
        steps = ["Apply these binary-morphology passes one after another, always "
                 "treating cells outside the image as 0 (background)."]
        for idx, (op, arg) in enumerate(metadata.passes, start=1):
            if op == "erode":
                desc = f"Erode using {_SE[arg]['word']}: a cell stays foreground only if the whole structuring element fits inside and every covered cell is foreground."
            elif op == "dilate":
                desc = f"Dilate using {_SE[arg]['word']}: a cell becomes foreground if any of the covered in-bounds cells is foreground."
            elif op == "open":
                desc = f"Open using {_SE[arg]['word']}: erode, then dilate, both with the same structuring element."
            elif op == "close":
                desc = f"Close using {_SE[arg]['word']}: dilate, then erode, both with the same structuring element."
            else:
                desc = f"Hit-miss transform detecting {_HM[arg]['word']}: the output cell is foreground only at exact matches of that foreground/background pattern entirely inside the image."
            steps.append(f"Pass {idx}: {desc}")
        steps.append("Report the final number of foreground cells (cells equal to 1). "
                     "The answer is a single integer.")
        return "\n".join([head, *steps])

    def score_answer(self, answer, entry):
        got = _parse_int(answer)
        if got is None:
            return 0.0
        return 1.0 if got == int(entry.answer) else 0.0
