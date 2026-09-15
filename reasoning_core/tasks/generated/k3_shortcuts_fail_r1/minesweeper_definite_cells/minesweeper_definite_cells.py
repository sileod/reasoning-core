import re
import random
from dataclasses import dataclass

import z3

from reasoning_core.template import Config, Entry, Task


@dataclass
class MinesweeperDefiniteCellsConfig(Config):
    rows: int = 4
    cols: int = 4
    n_mines: int = 3
    reveal_frac: float = 0.85
    max_attempts: int = 300

    def apply_difficulty(self, level):
        self.rows = 4 + level
        self.cols = 4 + level // 2
        self.n_mines = 3 + level
        self.reveal_frac = 0.85 - 0.02 * level
        self.max_attempts = 300 + 40 * level


def _neighbors(r, c, rows, cols):
    out = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                out.append((nr, nc))
    return out


def _classify(rows, cols, hidden, revealed_clues):
    vs = {h: z3.Bool("m%d_%d" % h) for h in hidden}
    solver = z3.Solver()
    for (r, c), clue in revealed_clues.items():
        terms = [vs[n] for n in _neighbors(r, c, rows, cols) if n in vs]
        solver.add(z3.Sum([z3.If(t, 1, 0) for t in terms]) == int(clue))
    mined = []
    safe = []
    for h in hidden:
        v = vs[h]
        solver.push()
        solver.add(v)
        mine_possible = solver.check() == z3.sat
        solver.pop()
        solver.push()
        solver.add(z3.Not(v))
        safe_possible = solver.check() == z3.sat
        solver.pop()
        if mine_possible and not safe_possible:
            mined.append(h)
        elif safe_possible and not mine_possible:
            safe.append(h)
    mined.sort()
    safe.sort()
    return mined, safe


def _format_answer(mined, safe):
    def fmt(cells):
        if not cells:
            return "None"
        return ",".join("(%d,%d)" % (r, c) for r, c in cells)

    return "Mined: %s Safe: %s" % (fmt(mined), fmt(safe))


def _parse_answer(answer):
    if not isinstance(answer, str):
        return None
    m = re.match(r"Mined:\s*(.*?)\s*Safe:\s*(.*)$", answer.strip(), re.DOTALL)
    if not m:
        return None
    mined_str, safe_str = m.group(1).strip(), m.group(2).strip()

    def parse_part(part):
        if part in ("None", "()", "[]"):
            return set()
        items = re.findall(r"\((\d+)\s*,\s*(\d+)\)", part)
        return {(int(a), int(b)) for a, b in items}

    return parse_part(mined_str), parse_part(safe_str)


class MinesweeperDefiniteCells(Task):
    summary = "Given a partially revealed grid with numeric clues, identify every cell mined in all consistent configurations and every cell provably safe; vary grid shapes, clue density, ambiguity; answer is two sorted cell lists."
    design_choice = "Generate grids by starting from a random mine placement and revealing all cells whose clue equals the number of adjacent mines, ensuring at least one ambiguous region."
    config_cls = MinesweeperDefiniteCellsConfig

    def generate_entry(self):
        rows = self.config.rows
        cols = self.config.cols
        n_mines = self.config.n_mines
        reveal_frac = self.config.reveal_frac
        cells = [(r, c) for r in range(rows) for c in range(cols)]
        assert 1 <= n_mines <= len(cells)

        for _ in range(self.config.max_attempts):
            mines = set(random.sample(cells, n_mines))
            non_mines = [c for c in cells if c not in mines]
            n_reveal = int(len(non_mines) * reveal_frac)
            n_reveal = max(0, min(n_reveal, len(non_mines)))
            revealed = set(random.sample(non_mines, n_reveal))
            hidden = [c for c in cells if c not in revealed]

            revealed_clues = {}
            for (r, c) in sorted(revealed):
                cnt = sum(1 for (nr, nc) in _neighbors(r, c, rows, cols) if (nr, nc) in mines)
                revealed_clues[(r, c)] = cnt

            mined, safe = _classify(rows, cols, hidden, revealed_clues)

            assert all(h in mines for h in mined), "definite mine must be a true mine"
            assert all(h not in mines for h in safe), "definite safe must be a true non-mine"
            assert not (set(mined) & set(safe)), "a cell cannot be both definite mine and safe"

            ambiguous = [h for h in hidden if h not in mined and h not in safe]
            if (mined or safe) and ambiguous:
                break
        else:
            raise RuntimeError(
                "MinesweeperDefiniteCells: failed to build a puzzle with both a definite "
                "and an ambiguous region after bounded attempts"
            )

        grid = [[revealed_clues.get((r, c)) for c in range(cols)] for r in range(rows)]
        return Entry(
            metadata={
                "rows": rows,
                "cols": cols,
                "grid": grid,
                "hidden": [tuple(h) for h in hidden],
                "mined": [tuple(h) for h in mined],
                "safe": [tuple(h) for h in safe],
            },
            answer=_format_answer(mined, safe),
        )

    def render_prompt(self, metadata):
        rows, cols = metadata["rows"], metadata["cols"]
        lines = []
        for r, row in enumerate(metadata["grid"]):
            tokens = []
            for c, v in enumerate(row):
                tokens.append("?" if v is None else str(v))
            lines.append(" ".join(tokens))
        grid_text = "\n".join(lines)

        return (
            "A partially revealed Minesweeper board has %d rows and %d columns. "
            "Cells showing a number 0-8 are revealed: the number is the count of mines among "
            "that cell's 8 neighbors (all adjacent cells in the 8 directions that exist on the "
            "board, including diagonals). Cells shown as '?' are hidden.\n"
            "\n"
            "Grid (rows top to bottom, columns left to right; the top-left cell is (0,0)):\n"
            "%s\n"
            "\n"
            "A placement of mines (chosen anywhere among the hidden '?' cells) is CONSISTENT if, "
            "for every revealed cell, the number shown equals how many of its 8 neighbors are mines.\n"
            "\n"
            "Considering only the hidden '?' cells:\n"
            "- a cell is DEFINITELY MINED if it is a mine in every consistent placement;\n"
            "- a cell is PROVABLY SAFE if it is NOT a mine in every consistent placement (clicking "
            "it would be safe);\n"
            "- any other hidden cell, whose mine status differs across consistent placements, is "
            "ambiguous and must not be listed.\n"
            "\n"
            "List (1) every DEFINITELY MINED hidden cell and (2) every PROVABLY SAFE hidden cell. "
            "Write each coordinate as (row,col); sort each list by row then column, comma-separated, "
            "using exactly this format, e.g.\n"
            "Mined: (0,1),(2,3) Safe: (1,1)\n"
            "Write None for an empty list, e.g.  Mined: None Safe: (0,2),(3,1)"
        ) % (rows, cols, grid_text)

    def score_answer(self, answer, entry):
        parsed = _parse_answer(answer)
        if parsed is None:
            return 0.0
        gold = (
            {(int(a), int(b)) for a, b in entry.metadata["mined"]},
            {(int(a), int(b)) for a, b in entry.metadata["safe"]},
        )
        return 1.0 if parsed == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'minesweeper_definite_cells (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/minesweeper_definite_cells',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
