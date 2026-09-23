"""Branch-and-bound optimal assignment tours on reduced cost matrices.

The generator builds a random square cost matrix, independently solves the
assignment problem with scipy (as a verifier), seeds a deterministic
branch-and-bound with a greedy incumbent, and records the ordered sequence of
zero cells it branches on.  The gold answer is the optimal tour value joined
with that branch order, so a reader who follows the stated algorithm reaches
the same value and the same branch order.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

import numpy as np

INF = 10 ** 9


@dataclass
class ReducedTourConfig(Config):
    size: int = 3
    hi: int = 40

    def apply_difficulty(self, level):
        self.size = 3 + level
        self.hi = 40 + 8 * level


def _reduce(mat):
    """Row-min then column-min reduction.  Returns (reduced, added) or (None, None)."""
    m = [row[:] for row in mat]
    nr = len(m)
    nc = len(m[0]) if nr else 0
    added = 0
    for i in range(nr):
        fin = [v for v in m[i] if v < INF]
        if not fin:
            return None, None
        mn = min(fin)
        added += mn
        m[i] = [v - mn if v < INF else v for v in m[i]]
    for j in range(nc):
        fin = [m[i][j] for i in range(nr) if m[i][j] < INF]
        if not fin:
            return None, None
        mn = min(fin)
        added += mn
        for i in range(nr):
            if m[i][j] < INF:
                m[i][j] -= mn
    return m, added


def _select_zero(m):
    """Return (bi, bj) original-sub-index of the max-penalty zero, ties by (i,j)."""
    k = len(m)
    zeros = [(i, j) for i in range(k) for j in range(k) if m[i][j] == 0]
    if not zeros:
        return None

    def pen(i, j):
        row = sorted(m[i][t] for t in range(k) if t != j and m[i][t] < INF)
        col = sorted(m[t][j] for t in range(k) if t != i and m[t][j] < INF)
        return (row[0] if row else INF) + (col[0] if col else INF)

    best = zeros[0]
    bp = -1
    for cell in sorted(zeros):
        p = pen(*cell)
        if p > bp:
            bp = p
            best = cell
    return best


def _greedy_incumbent(mat):
    """Row-by-row greedy complete assignment; deterministic seed for pruning."""
    n = len(mat)
    used = [False] * n
    cost = 0
    for i in range(n):
        best_j = None
        best_v = None
        for j in range(n):
            if not used[j]:
                v = mat[i][j]
                if best_v is None or v < best_v:
                    best_v = v
                    best_j = j
        used[best_j] = True
        cost += best_v
    return cost


def _branch_and_bound(mat, opt, maxit):
    """Deterministic DFS B&B.  Returns (best_found, branch_order) or (None, None)."""
    n = len(mat)
    best = [_greedy_incumbent(mat)]
    order = []
    it = [0]

    def dfs(a, lb, chosen, ridx, cidx):
        it[0] += 1
        if it[0] > maxit:
            raise RuntimeError("search too deep")
        if lb >= best[0]:
            return
        if not a:
            cost = sum(mat[r][c] for r, c in chosen)
            if cost < best[0]:
                best[0] = cost
            return
        m, re = _reduce(a)
        if m is None:
            return
        lb2 = lb + re
        if lb2 >= best[0]:
            return
        cell = _select_zero(m)
        if cell is None:
            return
        bi, bj = cell
        order.append((ridx[bi], cidx[bj]))
        include = [row[:bj] + row[bj + 1:] for row in m[:bi] + m[bi + 1:]]
        dfs(include, lb2, chosen + [(ridx[bi], cidx[bj])],
            ridx[:bi] + ridx[bi + 1:], cidx[:bj] + cidx[bj + 1:])
        ex = [row[:] for row in a]
        ex[bi][bj] = INF
        dfs(ex, lb, chosen, ridx, cidx)

    try:
        dfs(mat, 0, [], tuple(range(n)), tuple(range(n)))
    except RuntimeError:
        return None, None
    return best[0], order


def _make_answer(opt, order):
    return str(opt) + "|" + ",".join("(%d,%d)" % (r, c) for r, c in order)


class ReducedMatrixTourBranching(Task):
    summary = ("Branch-and-bound assignment tours on reduced matrices: subtract row/column "
               "minima, rank zeros by penalty, branch on the top zero, re-reduce and prune; "
               "answers are the optimal tour value joined to the branch order as zero-cell "
               "coordinates.")
    design_choice = "Answer format: return the optimal tour value as a single integer, with branch order encoded as a comma-separated list of zero-cell coordinates in the order they are branched on."

    config_cls = ReducedTourConfig
    task_version = 2

    def generate_entry(self):
        from scipy.optimize import linear_sum_assignment
        n = self.config.size
        hi = self.config.hi
        for _ in range(40):
            mat = [[random.randint(1, hi) for _ in range(n)] for _ in range(n)]
            arr = np.array(mat, dtype=np.int64)
            r, c = linear_sum_assignment(arr)
            opt = int(arr[r, c].sum())
            best, order = _branch_and_bound(mat, opt, maxit=120000)
            if best is None:
                continue
            if len(order) < n:
                continue
            assert best == opt, "B&B must independently reproduce the scipy optimum"
            assert opt >= 0
            return Entry(
                metadata={"matrix": mat, "size": n, "opt": opt},
                answer=_make_answer(opt, order),
            )
        raise RuntimeError("reduced_matrix_tour_branching: no admissible instance after retries")

    def render_prompt(self, metadata):
        n = metadata["size"]
        rows = "\n".join(" ".join(str(v) for v in row) for row in metadata["matrix"])
        return (
            f"Consider the {n}x{n} cost matrix where entry (i,j) is the cost of "
            f"assigning row i to column j; the goal is an optimal assignment (a "
            "one-to-one matching) that minimizes the total cost, with the cheapest "
            f"total called the optimal tour value.\n\n"
            f"Matrix (rows 0..{n-1}, columns 0..{n-1}):\n{rows}\n\n"
            "Solve it with branch-and-bound on the reduced matrix as follows. "
            "Reduce a matrix by subtracting the row minima then the column minima over the "
            "finite entries, and add the subtracted amounts to the node lower bound. "
            "For every zero cell, its penalty is the smallest finite entry in its row "
            "plus the smallest finite entry in its column, ignoring the zero itself. "
            "Branch on the zero of largest penalty; break ties by the lexicographic order "
            "of (row,column).  Its 'assign' child deletes that row and column from the "
            "reduced matrix and re-reduces; its 'exclude' child sets the cell to "
            "infinity and re-reduces.  Explore depth-first, always the assign child before "
            "the exclude child.  Initialize the incumbent (best complete assignment found so "
            "far) with a greedy row-by-row assignment: for each row in order pick the cheapest "
            "unused column and add its cost; update the incumbent whenever a leaf records a "
            "lower complete cost; and prune any node whose lower bound equals or exceeds the "
            "current incumbent.  A node with no remaining row or column records its complete "
            "assignment cost.\n\n"
            "Report the optimal tour value and the branch order of the zero cells (given as "
            "(row,column), zero-indexed) in the exact order they are branched on, as\n"
            "OPTIMAL_VALUE|(r,c),(r,c),...\n"
            "For example, for a value of 17 branching first on the zero at row 1 column 2 "
            "then at row 0 column 1, write 17|(1,2),(0,1)."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'reduced_matrix_tour_branching (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/reduced_matrix_tour_branching',
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
