import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'match_clear_cascade_resolution (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_multi_relation_integration_r4/match_clear_cascade_resolution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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


def _clean_board(rows, cols, letters):
    board = [['.'] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            bad = set()
            if c >= 2 and board[r][c - 1] == board[r][c - 2]:
                bad.add(board[r][c - 1])
            if r >= 2 and board[r - 1][c] == board[r - 2][c]:
                bad.add(board[r - 1][c])
            cand = [x for x in letters if x not in bad]
            board[r][c] = random.choice(cand)
    return board


def _simulate(start, rows, cols, stream, itermax):
    board = list(start)
    sp = 0
    total = 0
    for _ in range(itermax):
        matched = [False] * (rows * cols)
        any_m = False
        for r in range(rows):
            c = 0
            while c < cols:
                ch = board[r * cols + c]
                if ch == '.':
                    c += 1
                    continue
                j = c
                while j + 1 < cols and board[r * cols + j + 1] == ch:
                    j += 1
                if j - c + 1 >= 3:
                    any_m = True
                    for k in range(c, j + 1):
                        matched[r * cols + k] = True
                c = j + 1
        for c in range(cols):
            r = 0
            while r < rows:
                ch = board[r * cols + c]
                if ch == '.':
                    r += 1
                    continue
                j = r
                while j + 1 < rows and board[(j + 1) * cols + c] == ch:
                    j += 1
                if j - r + 1 >= 3:
                    any_m = True
                    for k in range(r, j + 1):
                        matched[k * cols + c] = True
                r = j + 1
        if not any_m:
            return ''.join(board), total, True
        for i in range(rows * cols):
            if matched[i]:
                board[i] = '.'
                total += 1
        for c in range(cols):
            col = [board[r * cols + c] for r in range(rows)]
            keep = [x for x in col if x != '.']
            for r in range(rows):
                board[r * cols + c] = '.'
            base = rows - len(keep)
            for idx, val in enumerate(keep):
                board[(base + idx) * cols + c] = val
        for c in range(cols):
            for r in range(rows):
                if board[r * cols + c] == '.':
                    if sp >= len(stream):
                        return None, total, False
                    board[r * cols + c] = stream[sp]
                    sp += 1
    return None, total, False


def _norm(s):
    return ''.join(ch for ch in str(s) if ch.isalnum()).upper()


@dataclass
class MatchClearConfig(Config):
    rows: int = 5
    cols: int = 5
    nletters: int = 6
    itermax: int = 200

    def apply_difficulty(self, level):
        self.rows = 5 + level
        self.cols = 4 + level
        self.nletters = max(4, 6 - level // 2)
        self.itermax = 200


class MatchClearCascadeResolver(Task):
    summary = ("Resolve swap-and-match boards of varied fixed sizes: apply a stated swap, then "
               "repeatedly clear every cell in a run of three or more identical tiles in a row or "
               "column, drop tiles, and refill from a stated stream to stability; answer is the final "
               "board concatenated as a single uppercase-letter string with '.' for empty cells.")
    config_cls = MatchClearConfig
    design_choice = ("Answer as a single canonical board string after full cascade, with tiles "
                     "encoded as single uppercase letters and empty cells as '.'; board dimensions "
                     "fixed per level.")

    def generate_entry(self):
        cfg = self.config
        itermax = cfg.itermax
        for _ in range(60):
            letters = [chr(ord('A') + i) for i in range(cfg.nletters)]
            board = _clean_board(cfg.rows, cfg.cols, letters)
            start = ''.join(''.join(row) for row in board)
            r1 = random.randrange(cfg.rows)
            c1 = random.randrange(cfg.cols)
            r2, c2 = r1, c1
            if random.random() < 0.5:
                r2 = r1 + (1 if r1 + 1 < cfg.rows else -1)
            else:
                c2 = c1 + (1 if c1 + 1 < cfg.cols else -1)
            swapped = list(start)
            swapped[r1 * cfg.cols + c1], swapped[r2 * cfg.cols + c2] = swapped[r2 * cfg.cols + c2], swapped[r1 * cfg.cols + c1]
            start_swapped = ''.join(swapped)
            stream = ''.join(random.choice(letters) for _ in range(cfg.rows * cfg.cols * 4))
            final_board, cleared, ok = _simulate(start_swapped, cfg.rows, cfg.cols, stream, itermax)
            if ok is False or final_board is None:
                continue
            if cleared <= 0:
                continue
            final2, _, ok2 = _simulate(start_swapped, cfg.rows, cfg.cols, stream, itermax)
            if ok2 is False or final2 != final_board:
                continue
            metadata = {
                'rows': cfg.rows,
                'cols': cfg.cols,
                'letters': ''.join(letters),
                'board': start,
                'swap': [(r1, c1), (r2, c2)],
                'stream': stream,
                'final_board': final_board,
                'cleared': cleared,
            }
            return Entry(metadata=metadata, answer=final_board)
        raise RuntimeError("match_clear_cascade: could not generate a valid cascade instance")

    def render_prompt(self, metadata):
        m = metadata
        rows, cols = m['rows'], m['cols']
        (r1, c1), (r2, c2) = m['swap']
        board_str = ' / '.join(m['board'][r * cols:(r + 1) * cols] for r in range(rows))
        return (
            f"A match-3 board has {rows} rows and {cols} columns; each tile is a single uppercase "
            f"letter and rows shown below are separated by '/'. First, the tiles at position "
            f"(row {r1}, col {c1}) and (row {r2}, col {c2}), counting from 0, are swapped. Then "
            f"repeat: clear every cell that belongs to a run of three or more identical tiles in a "
            f"row or a column, all at once; let the remaining tiles fall straight down within their "
            f"columns to fill gaps; and refill the empty cells at the tops of columns, left to right, "
            f"each column top to bottom, one tile at a time from the front of the refill stream below, "
            f"using tiles only as needed. Stop when no run of three or more remains anywhere. "
            f"Initial board: {board_str}. Refill stream: {m['stream']}. "
            f"State the final board after everything stabilizes as a single string with the first "
            f"row then the second and so on, uppercase letters for tiles and '.' for an empty cell."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = _norm(entry.answer)
        if not gold:
            return 0.0
        return 1.0 if _norm(answer) == gold else 0.0
