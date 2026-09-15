from dataclasses import dataclass

import random

from reasoning_core.template import Config, Entry, Task


@dataclass
class StoneCaptureConfig(Config):
    size: int = 9
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level
        self.size = 9 + 2 * level


def _neighbors(cell, size):
    r, c = cell
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < size and 0 <= nc < size:
            yield (nr, nc)


def _group_from(start, board, owner):
    size = len(board)
    seen = {start}
    stack = [start]
    while stack:
        for nb in _neighbors(stack.pop(), size):
            if nb not in seen and board[nb[0]][nb[1]] == owner:
                seen.add(nb)
                stack.append(nb)
    return seen


def _liberties(cells, board, size):
    libs = set()
    for c in cells:
        for nb in _neighbors(c, size):
            if board[nb[0]][nb[1]] == 0:
                libs.add(nb)
    return libs


def _build_scene(size):
    """Construct a board where a black move captures at least one white group."""
    for _ in range(60):
        board = [[0] * size for _ in range(size)]
        isize = random.randrange(1, max(2, size // 2 + 1))
        jsize = random.randrange(1, max(2, size // 2 + 1))
        r0 = random.randrange(0, size - isize)
        c0 = random.randrange(0, size - jsize)
        region = set()
        for dr in range(isize):
            for dc in range(jsize):
                region.add((r0 + dr, c0 + dc))

        border = set()
        for (r, c) in region:
            for nb in _neighbors((r, c), size):
                if nb not in region:
                    border.add(nb)
        if not border:
            continue

        move = random.choice(sorted(border))
        other_border = border - {move}
        for (r, c) in region:
            board[r][c] = 2
        for (r, c) in other_border:
            board[r][c] = 1

        played = _resolve_capture([row[:] for row in board], move, 1, size)
        if played is None or not played:
            continue

        empty = [(r, c) for r in range(size) for c in range(size)
                 if board[r][c] == 0 and (r, c) not in border and (r, c) not in region]
        random.shuffle(empty)
        dense = int(size * size * 0.30)
        for (r, c) in empty[:dense]:
            board[r][c] = random.choice((1, 2))
        return board, move
    raise RuntimeError("could not build a scene")


def _resolve_capture(board, stone, color, size):
    board[stone[0]][stone[1]] = color
    captured = set()
    for (r, c) in _neighbors(stone, size):
        if board[r][c] == 0 or board[r][c] == color:
            continue
        opp_group = _group_from((r, c), board, 3 - color)
        if not _liberties(opp_group, board, size):
            captured |= opp_group
    for (r, c) in captured:
        board[r][c] = 0
    if not captured and not _liberties(_group_from(stone, board, color), board, size):
        return None
    return captured


def _calculate_answer(board, stone, color, size):
    board[stone[0]][stone[1]] = color
    captured = set()
    for (r, c) in _neighbors(stone, size):
        owner = board[r][c]
        if owner == 0 or owner == color:
            continue
        opp_group = _group_from((r, c), board, 3 - color)
        if not _liberties(opp_group, board, size):
            captured |= opp_group
    removed = set(captured)
    for (r, c) in removed:
        board[r][c] = 0

    released_libs = set()
    for (r, c) in removed:
        for nb in _neighbors((r, c), size):
            if nb != stone and board[nb[0]][nb[1]] != 0:
                released_libs.add(nb)

    adjacent_groups = {}
    for (r, c) in _neighbors(stone, size):
        owner = board[r][c]
        if owner == 0:
            continue
        g = _group_from((r, c), board, owner)
        libs = _liberties(g, board, size) - {stone}
        adjacent_groups[owner] = sorted((rr, cc) for (rr, cc) in g)
    return captured, removed, released_libs, adjacent_groups


class StonePlacementCapture(Task):
    summary = ("Small Go boards of varying size (9/13/19) with random black/white "
               "groups; a legal stone placement captures an adjacent group or releases "
               "liberties; answer is the number of captured stones and the liberty "
               "count of each adjacent group after resolution.")
    design_choice = ("Instance boards vary in size (9x9, 13x13, 19x19) with random "
                     "group shapes, but answer format stays identical across sizes.")
    config_cls = StoneCaptureConfig

    def generate_entry(self):
        cfg = self.config

        for _ in range(40):
            raw, stone = _build_scene(cfg.size)
            board = [row[:] for row in raw]
            captured, removed, released_libs, adjacent_groups = _calculate_answer(
                board, stone, 1, cfg.size
            )

            num_captured = len(captured)
            num_released = len(released_libs)
            if num_captured == 0 and num_released == 0:
                continue

            adj = {}
            for (owner, cells) in adjacent_groups.items():
                g = {c for c in cells}
                libs = _liberties(g, board, cfg.size)
                adj[f"adj{owner}"] = len(libs)

            answer_parts = []
            if num_captured > 0:
                answer_parts.append(f"captured={num_captured}")
            if num_released > 0:
                answer_parts.append(f"released={num_released}")
            for owner in sorted(adj):
                answer_parts.append(f"{owner}={adj[owner]}")

            metadata = {
                "size": cfg.size,
                "board": [row[:] for row in raw],
                "stone": stone,
                "color": 1,
                "num_captured": num_captured,
                "num_released": num_released,
                "adj_libs": adj,
            }
            return Entry(metadata=metadata, answer="; ".join(answer_parts))
        raise RuntimeError("stone_placement_capture: could not build a good instance")

    def render_prompt(self, metadata):
        size = metadata["size"]
        stone = metadata["stone"]
        color = metadata["color"]
        color_name = "black" if color == 1 else "white"
        board = metadata["board"]
        lines = [f"Consider a {size}x{size} Go board. Black stones are 1, white stones "
                 f"are 2, empty points are 0."]
        for row in board:
            lines.append(" ".join(str(x) for x in row))
        lines.append(
            f"Black ({color_name}) plays a stone at row {stone[0]}, column {stone[1]}. "
            f"Under Go rules a captured group is removed and its liberties released. "
            f"Report, in this order: captured=N and released=N for the number of stones "
            f"captured and the number of liberties released (omit any that are 0), then "
            f"adj1=L and adj2=L for the number of liberties of each color's stones "
            f"adjacent to the played stone after resolution. Omit adj entries with no "
            f"adjacent stones of that color."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = set(entry.answer.split("; "))
        given = set(str(answer).split("; "))
        return 1.0 if gold == given else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'stone_placement_capture (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_specific_r1/stone_placement_capture',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
