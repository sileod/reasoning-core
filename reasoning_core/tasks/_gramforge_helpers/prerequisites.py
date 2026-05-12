"""
_gramforge_helpers/prerequisites.py
===================================
Shared infrastructure for the gramforge-backed tasks in reasoning_core.

Components:
  1. Fuzzer          — stable wrapper around gramforge generate()
  2. ExecutionResult — dataclass for sandbox output
  3. run_sandboxed   — exec() with timeout + stdout capture
  4. SemanticFilter  — post-execution triviality check
  5. TrivialityFilter— static AST-based triviality check
  6. ASTMetrics      — difficulty features
  7. DifficultyCalibrator

This file is a verbatim port of gramforge/tasks/prerequisites.py; logic
is unchanged.
"""

import io
import ast
import contextlib
import multiprocessing
import textwrap
import time
import random
from dataclasses import dataclass, field
from typing import Optional

from gramforge.grammars import tinypy_grammar
from gramforge import generate as _generate


DEFAULT_BUCKET_THRESHOLDS = (0.33, 0.66)


# ── 1. Fuzzer ────────────────────────────────────────────────────────────────

class Fuzzer:
    def __init__(self, grammar_fn=tinypy_grammar, min_depth=2, max_depth=10, seed=None):
        self.grammar_fn = grammar_fn
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.seed = seed
        self._grammar = grammar_fn()

    def sample(self, n: int = 1, seed=None) -> list:
        results = []
        effective_seed = seed if seed is not None else self.seed
        for i in range(n):
            s = None if effective_seed is None else hash((effective_seed, i)) % (2**31)
            node = _generate(self._grammar, max_depth=self.max_depth,
                             min_depth=self.min_depth, seed=s)
            results.append(node)
        return results

    def sample_code(self, n: int = 1, seed=None) -> list[str]:
        return [node @ 'py' for node in self.sample(n, seed=seed)]


# ── 2. ExecutionResult ───────────────────────────────────────────────────────

@dataclass
class ExecutionResult:
    success: bool
    stdout: str = ''
    error_type: Optional[str] = None
    error_msg: Optional[str] = None
    timed_out: bool = False
    elapsed_ms: float = 0.0
    captured: dict = field(default_factory=dict)

    @property
    def label(self) -> str:
        return 'runnable' if self.success else 'error'


# ── 3. Sandbox ───────────────────────────────────────────────────────────────

_UNSERIALIZABLE = '<unserializable>'


def _safe_serialize(value):
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        try:
            return type(value)(_safe_serialize(v) for v in value)
        except Exception:
            return _UNSERIALIZABLE
    if isinstance(value, dict):
        try:
            return {k: _safe_serialize(v) for k, v in value.items()
                    if isinstance(k, (str, int, float, bool))}
        except Exception:
            return _UNSERIALIZABLE
    return _UNSERIALIZABLE


def _sandbox_worker(code: str, result_queue: multiprocessing.Queue,
                    capture_vars: Optional[list] = None):
    buf = io.StringIO()
    t0 = time.perf_counter()
    exec_globals: dict = {}
    try:
        compiled = compile(code, '<sandbox>', 'exec')
        with contextlib.redirect_stdout(buf):
            exec(compiled, exec_globals)
        elapsed = (time.perf_counter() - t0) * 1000
        captured = {}
        if capture_vars:
            for var in capture_vars:
                if var in exec_globals:
                    captured[var] = _safe_serialize(exec_globals[var])
        result_queue.put({
            'success': True, 'stdout': buf.getvalue(),
            'error_type': None, 'error_msg': None,
            'timed_out': False, 'elapsed_ms': elapsed, 'captured': captured,
        })
    except Exception as exc:
        elapsed = (time.perf_counter() - t0) * 1000
        result_queue.put({
            'success': False, 'stdout': '',
            'error_type': type(exc).__name__, 'error_msg': str(exc)[:200],
            'timed_out': False, 'elapsed_ms': elapsed, 'captured': {},
        })


def run_sandboxed(code: str, timeout: float = 3.0,
                  capture_vars: Optional[list] = None) -> ExecutionResult:
    q: multiprocessing.Queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=_sandbox_worker,
                                args=(code, q, capture_vars), daemon=True)
    t0 = time.perf_counter()
    p.start()
    p.join(timeout=timeout)
    if p.is_alive():
        p.kill(); p.join()
        return ExecutionResult(success=False, error_type='TimeoutError',
                               error_msg=f'Exceeded {timeout}s',
                               timed_out=True,
                               elapsed_ms=(time.perf_counter() - t0) * 1000)
    if not q.empty():
        return ExecutionResult(**q.get_nowait())
    return ExecutionResult(success=False, error_type='ProcessError',
                           error_msg='Child process terminated unexpectedly',
                           elapsed_ms=(time.perf_counter() - t0) * 1000)


# ── 4. SemanticFilter ────────────────────────────────────────────────────────

class SemanticFilter:
    _TRIVIAL_RESULT_VALUES = (None,)

    def __init__(self, trivial_literals: Optional[tuple] = None):
        self.trivial_literals = (tuple(trivial_literals) if trivial_literals
                                 else self._TRIVIAL_RESULT_VALUES)

    def is_trivial(self, result: ExecutionResult,
                   entry_args: Optional[list] = None) -> bool:
        if not result.success:
            return False
        if result.stdout.strip():
            return False
        if not result.captured:
            return False
        if '_result' in result.captured:
            r = result.captured['_result']
            if r not in self.trivial_literals:
                if entry_args is None or r not in entry_args:
                    return False
        for name, value in result.captured.items():
            if name == '_result':
                continue
            if value not in self.trivial_literals:
                return False
        return True


# ── 5. TrivialityFilter ──────────────────────────────────────────────────────

@dataclass
class TrivialityPolicy:
    reject_empty: bool = True
    reject_single_assignment: bool = True
    reject_all_literal_prints: bool = True
    reject_identity_assignments: bool = True
    require_output: bool = True
    require_loops: bool = False
    require_top_level_execution: bool = False


class TrivialityFilter:
    def __init__(self, policy: Optional['TrivialityPolicy'] = None):
        self.policy = policy or TrivialityPolicy()

    def is_trivial(self, code: str) -> bool:
        try:
            tree = ast.parse(textwrap.dedent(code))
        except SyntaxError:
            return False
        stmts = tree.body
        p = self.policy
        if p.reject_empty and len(stmts) == 0:
            return True
        if p.reject_single_assignment and len(stmts) == 1 and isinstance(stmts[0], ast.Assign):
            return True
        prints = self._collect_prints(tree)
        assigns = self._collect_assigns(tree)
        if p.reject_all_literal_prints and prints and \
                all(self._is_literal(arg) for pr in prints for arg in pr.args):
            return True
        if p.reject_identity_assignments and assigns and \
                all(self._is_literal(v) for _, v in assigns):
            values = [ast.literal_eval(v) for _, v in assigns if self._is_literal(v)]
            str_values = [str(v) for v in values]
            if len(set(str_values)) == 1 and len(str_values) > 1:
                return True
        if p.require_output and not prints and not self._has_non_print_call(tree):
            return True
        if p.require_loops:
            if not any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree)):
                return True
        if p.require_top_level_execution:
            non_def = [s for s in stmts
                       if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef,
                                             ast.ClassDef, ast.Import, ast.ImportFrom))]
            if not non_def:
                return True
        return False

    def _collect_prints(self, tree):
        results = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == 'print'):
                results.append(node.value)
        return results

    def _has_non_print_call(self, tree) -> bool:
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            if isinstance(n.func, ast.Name) and n.func.id == 'print':
                continue
            return True
        return False

    def _collect_assigns(self, tree):
        results = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    results.append((target, node.value))
        return results

    def _is_literal(self, node):
        try:
            ast.literal_eval(node)
            return True
        except Exception:
            return False


# ── 6. ASTMetrics ────────────────────────────────────────────────────────────

@dataclass
class ASTMetrics:
    ast_height: int = 0
    num_nodes: int = 0
    num_leaves: int = 0
    num_variables: int = 0
    num_loops: int = 0
    nesting_depth: int = 0
    num_conditionals: int = 0
    has_print: bool = False
    difficulty_score: float = 0.0
    difficulty_bucket: str = 'easy'

    _NESTING_TYPES = (ast.For, ast.While, ast.If, ast.FunctionDef,
                      ast.AsyncFor, ast.AsyncFunctionDef, ast.With)

    @classmethod
    def from_code(cls, code: str,
                  thresholds: tuple = DEFAULT_BUCKET_THRESHOLDS) -> 'ASTMetrics':
        m = cls()
        try:
            tree = ast.parse(textwrap.dedent(code))
        except SyntaxError:
            return m
        all_nodes = list(ast.walk(tree))
        m.num_nodes = len(all_nodes)
        m.num_leaves = sum(1 for n in all_nodes
                           if not any(True for _ in ast.iter_child_nodes(n)))
        m.ast_height = cls._compute_height(tree)
        assigned_names = set()
        for node in all_nodes:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned_names.add(target.id)
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                assigned_names.add(node.target.id)
            elif isinstance(node, (ast.For, ast.AsyncFor)) and isinstance(node.target, ast.Name):
                assigned_names.add(node.target.id)
        m.num_variables = len(assigned_names)
        m.num_loops = sum(1 for n in all_nodes
                          if isinstance(n, (ast.For, ast.While, ast.AsyncFor)))
        m.num_conditionals = sum(1 for n in all_nodes if isinstance(n, ast.If))
        m.has_print = any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == 'print' for n in all_nodes
        )
        m.nesting_depth = cls._compute_nesting(tree)
        raw = (m.ast_height + 2 * m.num_loops + 3 * m.nesting_depth
               + m.num_variables + m.num_conditionals)
        m.difficulty_score = min(raw / 40.0, 1.0)
        m.difficulty_bucket = _bucket(m.difficulty_score, thresholds)
        return m

    @classmethod
    def from_node(cls, node, thresholds=DEFAULT_BUCKET_THRESHOLDS) -> 'ASTMetrics':
        try:
            code = node @ 'py'
        except Exception:
            return cls()
        return cls.from_code(code, thresholds=thresholds)

    @staticmethod
    def _compute_height(node, depth: int = 0) -> int:
        children = list(ast.iter_child_nodes(node))
        if not children:
            return depth
        return max(ASTMetrics._compute_height(c, depth + 1) for c in children)

    @classmethod
    def _compute_nesting(cls, node, current: int = 0) -> int:
        is_nesting = isinstance(node, cls._NESTING_TYPES)
        depth_here = current + 1 if is_nesting else current
        max_child = depth_here
        for child in ast.iter_child_nodes(node):
            max_child = max(max_child, cls._compute_nesting(child, depth_here))
        return max_child

    def to_dict(self) -> dict:
        return {
            'ast_height': self.ast_height, 'num_nodes': self.num_nodes,
            'num_leaves': self.num_leaves, 'num_variables': self.num_variables,
            'num_loops': self.num_loops, 'nesting_depth': self.nesting_depth,
            'num_conditionals': self.num_conditionals, 'has_print': self.has_print,
            'difficulty_score': round(self.difficulty_score, 4),
            'difficulty_bucket': self.difficulty_bucket,
        }


# ── 7. DifficultyCalibrator ──────────────────────────────────────────────────

class DifficultyCalibrator:
    def __init__(self, fuzzer: 'Fuzzer'):
        self.fuzzer = fuzzer
        self._thresholds: Optional[tuple] = None
        self._scores: list = []

    def calibrate(self, n_samples: int = 500, seed: int = 0,
                  lo_percentile: float = 33.0, hi_percentile: float = 66.0,
                  verbose: bool = True) -> tuple:
        rng = random.Random(seed)
        scores: list = []
        attempts = 0
        max_attempts = n_samples * 3
        while len(scores) < n_samples and attempts < max_attempts:
            attempts += 1
            try:
                node = self.fuzzer.sample(1, seed=rng.randint(0, 2**31))[0]
                code = node @ 'py'
            except Exception:
                continue
            m = ASTMetrics.from_code(code)
            if m.num_nodes > 0:
                scores.append(m.difficulty_score)
        if len(scores) < 10:
            raise RuntimeError(f"Only {len(scores)} samples for calibration.")
        scores.sort()
        lo_idx = int(len(scores) * lo_percentile / 100.0)
        hi_idx = int(len(scores) * hi_percentile / 100.0)
        self._scores = scores
        self._thresholds = (scores[lo_idx], scores[hi_idx])
        if verbose:
            print(f"  calibrated thresholds: {self._thresholds}")
        return self._thresholds

    @property
    def thresholds(self) -> tuple:
        if self._thresholds is None:
            raise RuntimeError("Call calibrate() first.")
        return self._thresholds


def _bucket(score: float, thresholds=DEFAULT_BUCKET_THRESHOLDS) -> str:
    lo, hi = thresholds
    if score < lo:
        return 'easy'
    elif score < hi:
        return 'medium'
    return 'hard'
