import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

MOVE_SETS = (
    ("right/down", ((1, 0), (0, 1))),
    ("right/down/diagonal", ((1, 0), (0, 1), (1, 1))),
    ("knight (monotone)", ((1, 2), (2, 1))),
)


def path_counts(grid, rows, cols, moves):
    counts = [[0] * cols for _ in range(rows)]
    if grid[0][0]:
        return counts
    counts[0][0] = 1
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                continue
            if grid[r][c]:
                continue
            total = 0
            for dr, dc in moves:
                pr, pc = r - dr, c - dc
                if 0 <= pr < rows and 0 <= pc < cols and not grid[pr][pc]:
                    total += counts[pr][pc]
            counts[r][c] = total
    return counts


@dataclass
class ConeConfig(Config):
    size: int = 4
    density: float = 0.2

    def apply_difficulty(self, level):
        self.size = 4 + 3 * min(1, level // 3)
        self.density = 0.20 + 0.035 * level


class GridPathCountCone(Task):
    summary = ("Obstacle grids under right/down, diagonal-added, or knight move sets with "
               "per-cell monotone path counts; one obstacle toggles on or off; answer is the "
               "cells whose counts change and the new count at the target corner.")
    design_choice = ("Answer format: output a compact string of changed-cell coordinates in "
                     "reading order followed by the new corner count, e.g., '2,3;4,5|17'.")
    config_cls = ConeConfig

    def generate_entry(self):
        size = self.config.size
        rows = cols = size
        move_name, moves = random.choice(MOVE_SETS)
        for _ in range(500):
            grid = [[False] * cols for _ in range(rows)]
            for r in range(rows):
                for c in range(cols):
                    if (r, c) != (0, 0) and (r, c) != (rows - 1, cols - 1):
                        if random.random() < self.config.density:
                            grid[r][c] = True
            base = path_counts(grid, rows, cols, moves)
            if base[rows - 1][cols - 1] == 0:
                continue
            add_cands = []
            remove_cands = []
            for r in range(rows):
                for c in range(cols):
                    if (r, c) == (0, 0) or (r, c) == (rows - 1, cols - 1):
                        continue
                    if grid[r][c]:
                        g2 = [row[:] for row in grid]
                        g2[r][c] = False
                        if path_counts(g2, rows, cols, moves)[rows - 1][cols - 1] != \
                           base[rows - 1][cols - 1]:
                            remove_cands.append((r, c))
                    else:
                        g2 = [row[:] for row in grid]
                        g2[r][c] = True
                        if path_counts(g2, rows, cols, moves)[rows - 1][cols - 1] != \
                           base[rows - 1][cols - 1]:
                            add_cands.append((r, c))
            if remove_cands and (not add_cands or random.random() < 0.5):
                tr, tc = random.choice(remove_cands)
                grid2 = [row[:] for row in grid]
                grid2[tr][tc] = False
                add_obstacle = False
            elif add_cands:
                tr, tc = random.choice(add_cands)
                grid2 = [row[:] for row in grid]
                grid2[tr][tc] = True
                add_obstacle = True
            else:
                continue
            before = base
            after = path_counts(grid2, rows, cols, moves)
            corner_after = after[rows - 1][cols - 1]
            if corner_after < 0:
                continue
            changed = [(r, c) for r in range(rows) for c in range(cols)
                       if before[r][c] != after[r][c]]
            if not changed:
                continue
            answer = ";".join(f"{r},{c}" for r, c in changed) + f"|{corner_after}"
            return Entry(metadata={
                "rows": rows,
                "cols": cols,
                "move_set": move_name,
                "grid": grid,
                "toggled": [tr, tc],
                "add_obstacle": add_obstacle,
                "changed": changed,
                "corner_before": before[rows - 1][cols - 1],
                "corner_after": corner_after,
            }, answer=answer)
        raise RuntimeError(f"grid_path_count_cone: no valid toggle after 500 grids")

    def render_prompt(self, metadata):
        rows, cols = metadata["rows"], metadata["cols"]
        move_name = metadata["move_set"]
        grid = metadata["grid"]
        tr, tc = metadata["toggled"]
        action = "an obstacle is placed at" if metadata["add_obstacle"] else "the obstacle at"
        cell_syms = {0: ".", 1: "#"}
        lines = []
        for r in range(rows):
            lines.append(" ".join(cell_syms[grid[r][c]] for c in range(cols)))
        board = "\n".join(lines)
        return (
            f"A robot starts at the top-left (row 0, column 0) and moves on a grid with "
            f"{move_name} moves. It can step to any of the cells its move set allows, staying "
            f"inside the grid and never landing on an obstacle (#). A monotone path is a sequence "
            f"of allowed steps that is non-decreasing in both row and column. The count at a cell "
            f"is the number of distinct monotone paths from the start to that cell.\n\n"
            f"The grid is {rows} rows by {cols} columns ('.' is open, '#' is an obstacle), rows "
            f"and columns indexed from 0. The target corner is the bottom-right cell "
            f"({rows - 1}, {cols - 1}).\n\n"
            f"{board}\n\n"
            f"Now {action} cell ({tr}, {tc}): a single obstacle is toggled (turned off if it was "
            f"on, on if it was off). All other cells are unchanged.\n"
            f"List every cell (row, col) in reading order (row by row, left to right) whose "
            f"path count changes, separated by ';', followed by '|' and the new path count at the "
            f"target corner. For example '2,3;4,5|17'."
        )

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == str(entry.answer).strip() else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'grid_path_count_cone (draw 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_specific_r1/grid_path_count_cone',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3020341981,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
