"""Small-forcing-seed tile assembly.

Model (aTAM-flavoured): an R x C board of numbered cells holds one tile type per
cell. Each tile exposes a (label, strength) glue pair on each of its four edges.
A cell seeded with its tile is present from the start; any unseeded cell may be
placed whenever the total strength of glue pairs it shares with already-placed
orthogonal neighbours reaches the temperature tau. Placement is monotone and
irreversible, so from any seed the set of ultimately filled cells is the unique
least fixed point of that rule -- every maximal legal attachment sequence (order
independent) terminates exactly there. A seed is *forcing* when that fixed point
is exactly the whole board. We return a smallest forcing seed, choosing the
lexicographically smallest among those that tie on size.
"""

import itertools
import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task

# direction indices: 0=up, 1=right, 2=down, 3=left; opposite is (i+2)%4
_DIRS = [(0, -1, 0), (1, 0, 1), (2, 1, 0), (3, 0, -1)]  # (dir, dr, dc)


def _closure(n_cells, cols, faces, tau, seed):
    """The unique terminal assembly reachable from `seed` (set of cell ids)."""
    placed = set(seed)
    rows = (n_cells - 1) // cols + 1
    changed = True
    while changed:
        changed = False
        for cell in range(n_cells):
            if cell in placed:
                continue
            r, c = divmod(cell, cols)
            total = 0
            for di, dr, dc in _DIRS:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < rows) or not (0 <= nc < cols):
                    continue
                neigh = nr * cols + nc
                if neigh not in placed:
                    continue
                (li, si) = faces[cell][di]
                (lj, _sj) = faces[neigh][(di + 2) % 4]
                if li == lj:
                    total += si
            if total >= tau:
                placed.add(cell)
                changed = True
    return placed


def _min_forcing_seed(rows, cols, faces, tau):
    """Smallest seeding (size, then lexicographic) whose closure is the board."""
    n = rows * cols
    target = set(range(n))
    for size in range(1, n + 1):
        for combo in itertools.combinations(range(n), size):
            if _closure(n, cols, faces, tau, combo) == target:
                return list(combo)
    return list(range(n))


def _build(rows, cols, label_count, strength_max, tau):
    faces = []
    for _ in range(rows * cols):
        cell = []
        for _face in range(4):
            label = random.randrange(label_count)
            strength = random.randint(1, strength_max)
            cell.append((label, strength))
        faces.append(cell)
    return faces


@dataclass
class TileSeedingConfig(Config):
    level_n: int = 4
    label_count: int = 3
    strength_max: int = 2
    tau: int = 1

    def apply_difficulty(self, level):
        # Monotone board sizes, all factorable into an R x C rectangle with R,C >= 2.
        self.level_n = [4, 6, 8, 9, 10, 12, 12][min(level, 6)]
        self.label_count = 3 + level // 2
        self.strength_max = 2
        self.tau = 1 + level // 4


# candidate rectangles with 2 <= rows <= cols and a small total, keyed by cell count
_SHAPES = {
    4: [(2, 2)],
    6: [(2, 3)],
    8: [(2, 4)],
    9: [(3, 3)],
    10: [(2, 5)],
    12: [(3, 4), (2, 6)],
}


class OrderIndependentTileSeeding(Task):
    summary = (
        "Choose seed cells under per-edge glue strengths and a temperature so every "
        "maximal legal attachment order fills exactly the board; return a smallest "
        "forcing seed (size, then lexicographically smallest) as sorted cell indices."
    )
    config_cls = TileSeedingConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = cfg.level_n + random.randint(0, 0)
        shapes = _SHAPES[n]
        rows, cols = random.choice(shapes)
        faces = _build(rows, cols, cfg.label_count, cfg.strength_max, cfg.tau)
        seed = _min_forcing_seed(rows, cols, faces, cfg.tau)
        assert _closure(rows * cols, cols, faces, cfg.tau, seed) == set(
            range(rows * cols)
        )
        assert 1 <= len(seed) <= rows * cols
        return Entry(
            metadata={
                "rows": int(rows),
                "cols": int(cols),
                "tau": int(cfg.tau),
                "faces": [
                    [[int(l), int(s)] for (l, s) in cell] for cell in faces
                ],
                "seed": [int(c) for c in seed],
            },
            answer=",".join(str(c) for c in seed),
        )

    def render_prompt(self, metadata):
        rows, cols, tau = metadata["rows"], metadata["cols"], metadata["tau"]
        n = rows * cols
        lines = [
            f"Tile-assembly growth runs on a {rows} by {cols} board whose {n} cells are "
            f"numbered row-major from 0 (cell at row r, column c has index r*{cols}+c).",
            f"Each cell holds its own tile; a tile's four edges (up, right, down, left) each "
            f"carry a glue label with a strength. Seeding a cell places its tile from the "
            f"start. At temperature {tau}, an unseeded cell may be placed once the total "
            f"strength of glue pairs it shares with already-placed orthogonal neighbours "
            f"(a pair counts only when the two tiles give the same label on the shared "
            f"edge, and contributes that tile's strength) reaches {tau}.",
            f"Placement may proceed in any order, and it continues until no further cell can "
            f"be placed, always staying inside the {rows} by {cols} board. The target is that "
            f"exactly all {n} cells end up placed.",
            "Tile glues (up, right, down, left; each 'label:strength'):",
        ]
        for c in range(n):
            r, col = divmod(c, cols)
            glues = metadata["faces"][c]
            parts = []
            for (lbl, st) in glues:
                parts.append(f"{lbl}:{st}")
            lines.append(
                f"cell {c} (row {r}, column {col}): {', '.join(parts)}"
            )
        lines.append("")
        lines.append(
            "Give the smallest set of cells such that seeding exactly those cells forces "
            "every maximal legal attachment sequence to place exactly all "
            f"{n} cells (and nothing else). If several smallest forcing seeds exist, give "
            "the lexicographically smallest (smallest first cell, then next, ...)."
        )
        lines.append("")
        lines.append(
            "Answer with only a comma-separated, sorted list of cell indices, e.g. '2,5' "
            "or '0,3,7'."
        )
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'order_independent_tile_seeding (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_planning_backtracking_r4/order_independent_tile_seeding',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1339177894,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
