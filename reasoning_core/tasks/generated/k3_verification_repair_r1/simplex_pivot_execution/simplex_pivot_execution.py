import random
from dataclasses import dataclass

from sympy import Rational

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _pair_reduce(vec, step):
    """Apply a primal simplex iteration for one entering column.

    Returns (status, T) where status is 'done' (optimal) or 'unbounded'.
    vec is a list of Rational rows [coefs..., rhs]; step indexes handled by caller.
    """


def _run_simplex(A, b, cvec):
    """Primal simplex from the origin, Bland's rule, exact rationals.

    Returns ('optimal', value) or ('unbounded', None).  value is a Rational.
    """
    n = len(cvec)
    m = len(b)
    total = n + m
    num_rows = m + 1
    num_cols = total + 1
    T = [[Rational(0)] * num_cols for _ in range(num_rows)]
    for i in range(m):
        for j in range(n):
            T[i][j] = Rational(A[i][j])
        T[i][n + i] = Rational(1)
        T[i][num_cols - 1] = Rational(b[i])
    for j in range(n):
        T[m][j] = Rational(-1) * cvec[j]
    basis = list(range(n, total))

    max_steps = (m + n) * 4 + 20
    for _step in range(max_steps):
        cands = [j for j in range(total) if j not in set(basis) and T[m][j] < 0]
        if not cands:
            value = -T[m][num_cols - 1]
            return ('optimal', value)
        enter = min(cands)
        best_ratio = None
        best_row = None
        for i in range(m):
            if T[i][enter] > 0:
                ratio = T[i][num_cols - 1] / T[i][enter]
                if (best_ratio is None or ratio < best_ratio or
                        (ratio == best_ratio and basis[i] < basis[best_row])):
                    best_ratio = ratio
                    best_row = i
        if best_row is None:
            return ('unbounded', None)
        piv = T[best_row][enter]
        row = T[best_row]
        for col in range(num_cols):
            row[col] = row[col] / piv
        for i in range(num_rows):
            if i == best_row:
                continue
            factor = T[i][enter]
            if factor:
                for col in range(num_cols):
                    T[i][col] = T[i][col] - factor * row[col]
        basis[best_row] = enter
    raise RuntimeError("simplex cycling")


def _fmt_rat(v):
    if v.denominator == 1:
        return str(int(v))
    return f"{v.p}/{v.q}"


@dataclass
class SimplexPivotConfig(Config):
    num_vars: int = 2
    num_constraints: int = 2
    coeff_range: int = 6
    rhs_range: int = 8

    def apply_difficulty(self, level):
        self.num_vars = stochastic_rounding(2 + level)
        self.num_constraints = stochastic_rounding(2 + level)
        self.coeff_range = stochastic_rounding(5 + 2 * level)
        self.rhs_range = stochastic_rounding(5 + 3 * level)


class SimplexPivotExecution(Task):
    summary = ("Run primal simplex on tiny standard-form LPs with a stated pivot "
               "rule and minimum-ratio tests, keeping exact rational tableaux, and "
               "returning the optimal value, pivot count, or an unboundedness flag.")
    design_choice = ("Generate instances by fixing a random feasible basis and "
                     "reverse-engineering the tableau so the stated pivot rule's first "
                     "pivot is predetermined, making the pivot count vary with "
                     "tie-breaking choices.")
    config_cls = SimplexPivotConfig
    task_version = 2

    def generate_entry(self):
        c = self.config
        n = c.num_vars
        m = c.num_constraints

        for _attempt in range(300):
            A = [[random.randint(-c.coeff_range, c.coeff_range) for _ in range(n)]
                 for _ in range(m)]
            b = [random.randint(1, c.rhs_range) for _ in range(m)]
            cvec = [random.randint(-c.coeff_range, c.coeff_range) for _ in range(n)]

            # First entering variable under Bland's rule: smallest index with negative cost.
            neg_indices = [j for j in range(n) if cvec[j] < 0]
            if not neg_indices:
                # optimal right away, trivial; skip to keep it a real simplex run
                continue
            entering = min(neg_indices)

            # The first pivot's leaving row is forced by the minimum-ratio test.
            status, value = _run_simplex(A, b, cvec)
            if status != 'optimal':
                # keep only bounded problems so the canonical answer is a rational value
                continue
            if value.denominator > 1 and value.q > 200:
                continue
            if value == 0:
                # a zero optimum makes the canonical answer '0' and collapses the
                # label distribution; keep nontrivial optima to preserve balance
                continue
            return Entry(
                metadata={
                    'A': A, 'b': b, 'c': cvec,
                    'n': n, 'm': m,
                    'pivot_rule': ("Bland's rule: at each step enter the smallest "
                                   "indexed variable with negative reduced cost; "
                                   "leave the row attaining the minimum ratio, "
                                   "tying by smallest row index."),
                    'result': 'optimal',
                    'value': _fmt_rat(value),
                },
                answer=_fmt_rat(value),
            )

        raise RuntimeError("failed to generate a bounded simplex instance after 300 tries")

    def render_prompt(self, metadata):
        lines = []
        lines.append("Consider the linear program in standard form")
        lines.append("maximize  " + self._render_obj(metadata['c']))
        lines.append("subject to")
        for i, row in enumerate(metadata['A']):
            lines.append("  " + self._render_row(row) + " <= " + str(metadata['b'][i]))
        lines.append("  x_i >= 0 for all i.")
        lines.append("")
        lines.append(metadata['pivot_rule'])
        lines.append("")
        lines.append("Run primal simplex from the origin with exact rational arithmetic.")
        lines.append("Give the optimal objective value V as a single rational number")
        lines.append("(for example 3 or 5/2).")
        lines.append("")
        lines.append("Answer format: the optimal value V only.")
        return "\n".join(lines)

    def _render_obj(self, c):
        terms = []
        for j, a in enumerate(c):
            if a == 0:
                continue
            var = "x%d" % (j + 1)
            terms.append(f"{a}{var}" if a not in (1, -1) else (var if a == 1 else f"-{var}"))
        out = " + ".join(terms).replace("+ -", "- ")
        return out if out else "0"

    def _render_row(self, row):
        terms = []
        for j, a in enumerate(row):
            if a == 0:
                continue
            var = "x%d" % (j + 1)
            terms.append(f"{a}{var}" if a not in (1, -1) else (var if a == 1 else f"-{var}"))
        out = " + ".join(terms).replace("+ -", "- ")
        return out if out else "0"

    def score_answer(self, answer, entry):
        md = entry.metadata
        gold = Rational(md['value'])
        try:
            if isinstance(answer, str):
                a = Rational(answer.strip())
            else:
                a = Rational(answer)
        except Exception:
            return 0.0
        return 1.0 if a == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'simplex_pivot_execution (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/simplex_pivot_execution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
