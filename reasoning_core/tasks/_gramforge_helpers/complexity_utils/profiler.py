"""
complexity_profiler.py
======================
Empirical complexity measurement via AST instrumentation and op counting.

Given a Python program, this module:
  1. Rewrites the AST to count primitive operations (BinOp, Compare, Subscript, Call)
  2. Executes the instrumented program at multiple values of `n`
  3. Fits candidate complexity curves to op-count(n) data
  4. Classifies to the best-fitting curve: O(1) / O(log n) / O(n) / O(n log n) / O(n^2)

The profiler is the empirical ground-truth oracle for complexity labels.
No claim about a program's complexity is trusted unless the profiler confirms it.
"""

import ast
import math
import textwrap
from dataclasses import dataclass, field
from typing import Optional


# ── Default profile points ────────────────────────────────────────────────────
# Chosen to span a wide range so O(log n) and O(n log n) separate cleanly
# from their neighbors. Larger ranges give cleaner fits but cost generation time.

DEFAULT_NS = [30, 100, 300, 1000, 3000]


# ── Candidate complexity curves ───────────────────────────────────────────────
# Each curve is a function of n that returns a "shape" value; op-counts
# are fit as counts ≈ a + b * shape(n). The model with best R² wins.

def _shape_const(n):   return 1.0
def _shape_log(n):     return math.log(n) if n > 1 else 0.0
def _shape_linear(n):  return float(n)
def _shape_nlogn(n):   return n * math.log(n) if n > 1 else 0.0
def _shape_quad(n):    return float(n) * n


_CANDIDATE_MODELS = [
    ('O(1)',       _shape_const),
    ('O(log n)',   _shape_log),
    ('O(n)',       _shape_linear),
    ('O(n log n)', _shape_nlogn),
    ('O(n^2)',     _shape_quad),
]


# Minimum R² to accept a classification. Below this, label is 'unknown'.
MIN_R_SQUARED = 0.98


# ── Op-counting AST instrumentation ───────────────────────────────────────────

class _OpCounterInstrumenter(ast.NodeTransformer):
    """
    Rewrites an AST so that every BinOp, Compare, Subscript, and Call
    increments a global counter `__op_count`.

    Transformation (conceptual):
        x + y              →   (__op_count_inc(), x + y)[1]
        a < b              →   (__op_count_inc(), a < b)[1]
        lst[i]             →   (__op_count_inc(), lst[i])[1]
        foo()              →   (__op_count_inc(), foo())[1]

    The counter increment is wrapped in a tuple so the original expression's
    value is preserved.
    """

    COUNTED_NODES = (ast.BinOp, ast.Compare, ast.Subscript, ast.Call)

    def _wrap_with_counter(self, node: ast.expr) -> ast.expr:
        inc_call = ast.Call(
            func=ast.Name(id='__op_count_inc', ctx=ast.Load()),
            args=[], keywords=[],
        )
        tuple_node = ast.Tuple(elts=[inc_call, node], ctx=ast.Load())
        subscript = ast.Subscript(
            value=tuple_node,
            slice=ast.Constant(value=1),
            ctx=ast.Load(),
        )
        return ast.copy_location(subscript, node)

    def visit_BinOp(self, node):
        self.generic_visit(node)
        return self._wrap_with_counter(node)

    def visit_Compare(self, node):
        self.generic_visit(node)
        return self._wrap_with_counter(node)

    def visit_Subscript(self, node):
        # Avoid double-wrapping our own generated subscripts
        if isinstance(node.value, ast.Tuple) and len(node.value.elts) == 2 \
                and isinstance(node.value.elts[0], ast.Call) \
                and isinstance(node.value.elts[0].func, ast.Name) \
                and node.value.elts[0].func.id == '__op_count_inc':
            return node
        self.generic_visit(node)
        return self._wrap_with_counter(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == '__op_count_inc':
            return node
        self.generic_visit(node)
        return self._wrap_with_counter(node)


def instrument(code: str) -> str:
    """
    Return the given Python code rewritten so every primitive operation
    increments a global counter `__op_count`.
    """
    tree = ast.parse(textwrap.dedent(code))
    instrumented = _OpCounterInstrumenter().visit(tree)
    ast.fix_missing_locations(instrumented)
    return ast.unparse(instrumented)


# ── Profile result ────────────────────────────────────────────────────────────

@dataclass
class ProfileResult:
    """
    The result of profiling a parametric program at multiple values of n.

    Attributes
    ----------
    counts : dict[int, int]
        Operation count at each n.
    slope : float
        Legacy log-log regression slope (approximate growth exponent).
        Kept for backward compatibility / reporting.
    intercept : float
        Log-log regression intercept.
    r_squared : float
        R² of the best-fitting candidate model.
    label : str
        Best-fitting complexity label: 'O(1)' / 'O(log n)' / 'O(n)' /
        'O(n log n)' / 'O(n^2)' / 'unknown'.
    ns : list[int]
        The n values that were probed.
    model_r_squared : dict[str, float]
        R² per candidate model, for transparency.
    """
    counts: dict = field(default_factory=dict)
    slope: float = 0.0
    intercept: float = 0.0
    r_squared: float = 0.0
    label: str = 'unknown'
    ns: list = field(default_factory=list)
    model_r_squared: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'counts':          {str(k): v for k, v in self.counts.items()},
            'slope':           round(self.slope, 4),
            'intercept':       round(self.intercept, 4),
            'r_squared':       round(self.r_squared, 4),
            'label':           self.label,
            'ns':              self.ns,
            'model_r_squared': {k: round(v, 4) for k, v in self.model_r_squared.items()},
        }


# ── Profiler ──────────────────────────────────────────────────────────────────

class ComplexityProfiler:
    """
    Measures the empirical complexity of a parametric Python program.

    The program must define a callable `run(n)` or whatever the caller
    specifies as entry_point. In Task 3 v2 we use `solve` by default,
    since all slot-filled templates declare `def solve(n: int)`.

    Usage
    -----
    >>> profiler = ComplexityProfiler(entry_point='solve')
    >>> result = profiler.profile(code)
    >>> result.label      # 'O(n)'
    """

    def __init__(self, ns: list = None, entry_point: str = 'solve',
                 min_r_squared: float = MIN_R_SQUARED):
        self.ns = ns or DEFAULT_NS
        self.entry_point = entry_point
        self.min_r_squared = min_r_squared

    def profile(self, code: str) -> ProfileResult:
        instrumented = instrument(code)
        counts: dict[int, int] = {}
        for n in self.ns:
            counts[n] = self._run_and_count(instrumented, n)

        result = ProfileResult(counts=dict(counts), ns=list(self.ns))
        result.slope, result.intercept, _ = self._fit_loglog(counts)
        result.label, result.r_squared, result.model_r_squared = \
            self._classify_by_curve_fit(counts)
        return result

    # ── internals ─────────────────────────────────────────────────────────

    def _run_and_count(self, instrumented_code: str, n: int) -> int:
        import io, contextlib
        env = self._make_env()
        with contextlib.redirect_stdout(io.StringIO()):
            exec(instrumented_code, env)
            if self.entry_point not in env:
                raise ValueError(f"Program has no '{self.entry_point}' function")
            env['__op_count'] = 0
            env[self.entry_point](n)
        return env['__op_count']

    def _make_env(self) -> dict:
        env: dict = {'__op_count': 0}

        def _inc():
            env['__op_count'] += 1
            return None

        env['__op_count_inc'] = _inc
        return env

    def _fit_loglog(self, counts: dict) -> tuple[float, float, float]:
        """Log-log regression (legacy; kept for the `slope` field)."""
        xs = [math.log(n) for n, c in counts.items() if c > 0]
        ys = [math.log(c) for n, c in counts.items() if c > 0]
        if len(xs) < 2:
            return 0.0, 0.0, 0.0
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        den = sum((x - mean_x) ** 2 for x in xs)
        if den == 0:
            return 0.0, mean_y, 0.0
        slope = num / den
        intercept = mean_y - slope * mean_x
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
        ss_tot = sum((y - mean_y) ** 2 for y in ys)
        r_sq = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
        return slope, intercept, r_sq

    def _classify_by_curve_fit(self, counts: dict) -> tuple:
        """
        Fit counts ≈ a + b * shape(n) for each candidate model.
        Return (best_label, best_r_squared, all_r_squared).
        """
        # Special case: all counts equal → O(1) even if numerical issues arise
        unique_counts = set(counts.values())
        if len(unique_counts) == 1:
            r_all = {label: 1.0 if label == 'O(1)' else 0.0
                     for label, _ in _CANDIDATE_MODELS}
            return 'O(1)', 1.0, r_all

        ns = list(counts.keys())
        ys = [counts[n] for n in ns]

        r_all: dict = {}
        best_label, best_r = 'unknown', -math.inf
        for label, shape_fn in _CANDIDATE_MODELS:
            xs = [shape_fn(n) for n in ns]
            r2 = self._r_squared(xs, ys)
            r_all[label] = r2
            if r2 > best_r:
                best_r, best_label = r2, label

        if best_r < self.min_r_squared:
            return 'unknown', best_r, r_all
        return best_label, best_r, r_all

    @staticmethod
    def _r_squared(xs: list, ys: list) -> float:
        """R² of least-squares linear fit ys ≈ a + b*xs."""
        n = len(xs)
        if n < 2:
            return 0.0
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        den_x = sum((x - mean_x) ** 2 for x in xs)
        if den_x == 0:
            return 0.0
        b = num / den_x
        a = mean_y - b * mean_x
        ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
        ss_tot = sum((y - mean_y) ** 2 for y in ys)
        if ss_tot == 0:
            return 1.0
        return 1.0 - (ss_res / ss_tot)
