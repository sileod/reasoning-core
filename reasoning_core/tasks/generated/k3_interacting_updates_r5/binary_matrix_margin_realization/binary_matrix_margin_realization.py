import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class BinaryMatrixMarginConfig(Config):
    rows: int = 4
    cols: int = 4
    max_pins: int = 2

    def apply_difficulty(self, level):
        self.rows = 3 + min(level, 4)
        self.cols = 3 + min(level, 4)
        self.max_pins = 1 + min(level, 3)


def _count_realizations(row_sums, col_sums, pins, n, m, limit=2000):
    from functools import lru_cache

    pins = dict(pins)
    r = row_sums[:]
    c = col_sums[:]
    for (i, j), v in pins.items():
        r[i] -= v
        c[j] -= v
    if any(x < 0 for x in r) or any(x < 0 for x in c):
        return 0
    if sum(r) != sum(c):
        return 0
    colsum = tuple(c)
    cols_by_row = [tuple(j for j in range(m) if (i, j) not in pins) for i in range(n)]

    @lru_cache(maxsize=None)
    def rec(row, colsum):
        if row == n:
            return 1 if sum(colsum) == 0 else 0
        rem_r = r[row]
        total = 0
        cols = cols_by_row[row]
        for csel in _choose(cols, rem_r):
            if any(colsum[j] <= 0 for j in csel):
                continue
            new = list(colsum)
            for j in csel:
                new[j] -= 1
            total += rec(row + 1, tuple(new))
            if total > limit:
                return total
        return total

    return rec(0, colsum)


def _choose(cols, k):
    if k < 0 or k > len(cols):
        return []
    out = []

    def comb(start, cur):
        if len(cur) == k:
            out.append(tuple(cur))
            return
        if len(out) > 2000:
            return
        for idx in range(start, len(cols)):
            cur.append(cols[idx])
            comb(idx + 1, cur)
            cur.pop()

    comb(0, [])
    return out


def _has_alternating_swap(mat, pinmap, n, m):
    for i1 in range(n):
        for i2 in range(i1 + 1, n):
            for j1 in range(m):
                for j2 in range(j1 + 1, m):
                    cells = {(i1, j1), (i1, j2), (i2, j1), (i2, j2)}
                    if cells & set(pinmap):
                        continue
                    a = mat[i1][j1]
                    b = mat[i1][j2]
                    c = mat[i2][j1]
                    d = mat[i2][j2]
                    if a == d and b == c and a != b:
                        return True
    return False


class BinaryMatrixMarginRealization(Task):
    summary = "Fill a binary matrix from row and column sums, with optional pinned cells: place each row's ones into its most-demanded columns while auditing residual feasibility; answer the canonical filling, infeasible, or non-unique."
    config_cls = BinaryMatrixMarginConfig

    design_choice = "Pin cells by row-column coordinates with fixed values, forcing the solver to route around them while preserving row/column sums."

    def _gen_pins(self, n, m, count):
        cells = set()
        guard = 0
        while len(cells) < count and guard < n * m * 4:
            i = random.randrange(n)
            j = random.randrange(m)
            cells.add((i, j))
            guard += 1
        return sorted(cells)

    def _gen_unique(self, n, m):
        density = random.choice([0.12, 0.88])
        for _ in range(200):
            pins = self._gen_pins(n, m, random.randrange(0, self.config.max_pins + 1))
            pinmap = {(i, j): 1 for (i, j) in pins}
            mat = [[0] * m for _ in range(n)]
            for (i, j) in pins:
                mat[i][j] = 1
            for i in range(n):
                for j in range(m):
                    if mat[i][j] == 0 and random.random() < density:
                        mat[i][j] = 1
            row_sums = [sum(row) for row in mat]
            col_sums = [sum(mat[i][j] for i in range(n)) for j in range(m)]
            count = _count_realizations(row_sums, col_sums, pinmap, n, m)
            if count == 1:
                return row_sums, col_sums, pins, mat
        return None

    def generate_entry(self):
        n = self.config.rows
        m = self.config.cols
        for _ in range(60):
            want_unique = random.random() < 0.87
            if want_unique:
                res = self._gen_unique(n, m)
                if res is None:
                    continue
                row_sums, col_sums, pins, full = res
                pin_list = [[i, j, 1] for (i, j) in pins]
                meta = {
                    "rows": n,
                    "cols": m,
                    "row_sums": row_sums,
                    "col_sums": col_sums,
                    "pins": pin_list,
                    "mode": "pinned" if pins else "unpinned",
                    "answer_type": "unique",
                    "filling": [list(x) for x in full],
                }
                return Entry(metadata=meta, answer=_format_matrix(full))
            else:
                res = self._gen_nonunique(n, m)
                if res is None:
                    continue
                row_sums, col_sums, pins = res
                meta = {
                    "rows": n,
                    "cols": m,
                    "row_sums": row_sums,
                    "col_sums": col_sums,
                    "pins": [[i, j, 1] for (i, j) in pins],
                    "mode": "pinned" if pins else "unpinned",
                    "answer_type": "non-unique",
                }
                return Entry(metadata=meta, answer="non-unique")
        raise RuntimeError("could not construct instance")

    def _gen_nonunique(self, n, m):
        guard = 0
        while guard < 200:
            guard += 1
            pins = self._gen_pins(n, m, random.randrange(0, self.config.max_pins + 1))
            pinmap = {(i, j): 1 for (i, j) in pins}
            # random mid-density matrix avoiding pins
            mat = [[0] * m for _ in range(n)]
            for (i, j) in pins:
                mat[i][j] = 1
            for i in range(n):
                for j in range(m):
                    if (i, j) not in pinmap and random.random() < 0.5:
                        mat[i][j] = 1
            if not _has_alternating_swap(mat, pinmap, n, m):
                continue
            row_sums = [sum(row) for row in mat]
            col_sums = [sum(mat[i][j] for i in range(n)) for j in range(m)]
            count = _count_realizations(row_sums, col_sums, pinmap, n, m)
            if count is not None and count > 1:
                return row_sums, col_sums, pins
        return None

    def render_prompt(self, metadata):
        n = metadata["rows"]
        m = metadata["cols"]
        rs = " ".join(map(str, metadata["row_sums"]))
        cs = " ".join(map(str, metadata["col_sums"]))
        lines = [
            f"Consider an {n}-by-{m} binary matrix, where every entry is either 0 or 1.",
            f"Its row sums are: {rs}",
            f"Its column sums are: {cs}",
        ]
        pins = metadata["pins"]
        if pins:
            pin_desc = ", ".join(f"row {p[0]} column {p[1]} = {p[2]}" for p in pins)
            lines.append(f"The following cells are fixed in advance: {pin_desc}.")
        lines.append(
            "Find a binary matrix satisfying these row and column sums (and the fixed cells, if any). "
            "Fill each row by placing its ones into the columns with the largest remaining demand. "
            "If exactly one such matrix exists, answer the matrix with one row per line and entries "
            "separated by spaces. If more than one distinct matrix satisfies the constraints, write "
            "exactly 'non-unique'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        return _score(metadata, answer)


def _format_matrix(mat):
    return "\n".join(" ".join(map(str, row)) for row in mat)


def _parse_matrix(answer):
    answer = answer.strip()
    if not answer:
        return None
    try:
        rows = [list(map(int, line.split())) for line in answer.split("\n") if line.strip()]
        if not rows:
            return None
        m = len(rows[0])
        for row in rows:
            if len(row) != m or any(v not in (0, 1) for v in row):
                return None
        return rows
    except ValueError:
        return None


def _score(metadata, answer):
    a = answer.strip()
    expected_type = metadata.get("answer_type")
    if expected_type == "non-unique":
        return 1.0 if a == "non-unique" else 0.0
    if expected_type == "unique":
        rows = _parse_matrix(answer)
        if rows is None:
            return 0.0
        if [sum(r) for r in rows] != metadata["row_sums"]:
            return 0.0
        n = metadata["rows"]
        m = metadata["cols"]
        cols = [sum(rows[i][j] for i in range(n)) for j in range(m)]
        if cols != metadata["col_sums"]:
            return 0.0
        for (i, j, v) in metadata["pins"]:
            if rows[i][j] != v:
                return 0.0
        return 1.0
    return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'binary_matrix_margin_realization (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_interacting_updates_r5/binary_matrix_margin_realization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
