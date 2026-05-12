# reasoning_core/tasks/refactoring.py
"""
Refactoring recognition task.

Given two semantically equivalent Python programs (same stdout), identify
which AST-level transformation was applied to convert the first into the
second, chosen from:

    dead_code_injection   — an unused variable assignment was inserted
    redundant_assignment  — an existing literal assignment was duplicated
    variable_inlining     — a single-use literal variable was inlined
    constant_unfolding    — an integer constant was split into a + b
"""

import ast
import random
import textwrap
from collections import Counter
from dataclasses import dataclass
from typing import Optional

from easydict import EasyDict as edict
from gramforge import generate as _generate

from reasoning_core.template import Task, Problem, Config

from ._gramforge_helpers.grammars import pygram_grammar
from ._gramforge_helpers.prerequisites import (
    Fuzzer, TrivialityFilter, run_sandboxed, ASTMetrics,
)
from ._gramforge_helpers.pygram_adapter import (
    add_entry_call, PYGRAM_TRIVIALITY_POLICY,
)


TRANSFORMATIONS = [
    'dead_code_injection',
    'redundant_assignment',
    'variable_inlining',
    'constant_unfolding',
]


# ── Transformation engine (AST-based) ─────────────────────────────────────────

class _TransformationEngine:
    """Applies semantics-preserving AST-level transformations."""

    STRATEGIES = TRANSFORMATIONS

    def __init__(self, rng: random.Random):
        self.rng = rng

    def transform_with_strategy(self, code: str, strategy: str) -> Optional[str]:
        if strategy not in self.STRATEGIES:
            return None
        return getattr(self, f'_apply_{strategy}')(code)

    # -- helpers --

    def _get_scopes(self, tree: ast.Module) -> list:
        """Statement-list scopes we can modify: module body + function bodies."""
        scopes = [tree.body]
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scopes.append(node.body)
        return scopes

    def _fresh_name(self, existing: set) -> Optional[str]:
        import keyword
        blocked = existing | set(keyword.kwlist) | {'print', 'range', 'len'}
        for c in 'abcdefghijklmnopqrstuvwxyz':
            if c not in blocked:
                return c
        return None

    # -- transformations --

    def _apply_dead_code_injection(self, code: str) -> Optional[str]:
        tree = ast.parse(textwrap.dedent(code))
        existing = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        fresh = self._fresh_name(existing)
        if fresh is None:
            return None
        scopes = self._get_scopes(tree)
        viable = [s for s in scopes
                  if any(isinstance(stmt, ast.Assign) for stmt in s)]
        if not viable:
            return None
        target_scope = self.rng.choice(viable)
        assign_positions = [i for i, s in enumerate(target_scope)
                            if isinstance(s, ast.Assign)]
        insert_after = self.rng.choice(assign_positions)
        val = self.rng.randint(1, 15)
        dead_stmt = ast.parse(f'{fresh} = {val}').body[0]
        ast.fix_missing_locations(dead_stmt)
        target_scope.insert(insert_after + 1, dead_stmt)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)

    def _apply_redundant_assignment(self, code: str) -> Optional[str]:
        tree = ast.parse(textwrap.dedent(code))
        scopes = self._get_scopes(tree)
        candidates = []
        for scope in scopes:
            for i, stmt in enumerate(scope[:-1]):
                if (isinstance(stmt, ast.Assign)
                        and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Name)
                        and isinstance(stmt.value, ast.Constant)):
                    candidates.append((scope, i))
        if not candidates:
            return None
        scope, idx = self.rng.choice(candidates)
        dup = ast.parse(ast.unparse(scope[idx])).body[0]
        ast.fix_missing_locations(dup)
        scope.insert(idx, dup)
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)

    def _apply_variable_inlining(self, code: str) -> Optional[str]:
        tree = ast.parse(textwrap.dedent(code))
        scopes = self._get_scopes(tree)
        candidates = []
        for scope in scopes:
            for i, stmt in enumerate(scope):
                if not (isinstance(stmt, ast.Assign)
                        and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Name)
                        and isinstance(stmt.value, ast.Constant)):
                    continue
                var = stmt.targets[0].id
                val = stmt.value.value
                rest_nodes = []
                for later_stmt in scope[i+1:]:
                    rest_nodes.extend(ast.walk(later_stmt))
                uses = [n for n in rest_nodes
                        if isinstance(n, ast.Name) and n.id == var
                        and isinstance(n.ctx, ast.Load)]
                if len(uses) == 1:
                    candidates.append((scope, i, var, val))
        if not candidates:
            return None
        target_scope, idx, var, val = self.rng.choice(candidates)

        class _Inliner(ast.NodeTransformer):
            def __init__(self, var, val):
                self.var = var; self.val = val; self.done = False
            def visit_Name(self, node):
                if (node.id == self.var
                        and isinstance(node.ctx, ast.Load)
                        and not self.done):
                    self.done = True
                    return ast.Constant(value=self.val)
                return node

        target_scope.pop(idx)
        inliner = _Inliner(var, val)
        for later_stmt in target_scope[idx:]:
            inliner.visit(later_stmt)
            if inliner.done:
                break
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)

    def _apply_constant_unfolding(self, code: str) -> Optional[str]:
        tree = ast.parse(textwrap.dedent(code))
        scopes = self._get_scopes(tree)
        candidates = []
        for scope in scopes:
            for stmt in scope:
                if (isinstance(stmt, ast.Assign)
                        and len(stmt.targets) == 1
                        and isinstance(stmt.value, ast.Constant)
                        and isinstance(stmt.value.value, int)
                        and stmt.value.value >= 2):
                    candidates.append(stmt)
        if not candidates:
            return None
        stmt = self.rng.choice(candidates)
        n = stmt.value.value
        a = self.rng.randint(1, n - 1)
        b = n - a
        new_val = ast.BinOp(
            left=ast.Constant(value=a),
            op=ast.Add(),
            right=ast.Constant(value=b),
        )
        ast.copy_location(new_val, stmt.value)
        stmt.value = new_val
        ast.fix_missing_locations(tree)
        return ast.unparse(tree)


# ── Diff helper (for metadata) ────────────────────────────────────────────────

def _normalize_whitespace(code: str) -> str:
    try:
        return ast.unparse(ast.parse(code))
    except SyntaxError:
        return code


def _count_changed_lines(a: str, b: str) -> int:
    a_norm = _normalize_whitespace(a)
    b_norm = _normalize_whitespace(b)
    count_a = Counter(a_norm.strip().splitlines())
    count_b = Counter(b_norm.strip().splitlines())
    added   = sum((count_b - count_a).values())
    removed = sum((count_a - count_b).values())
    return max(added, removed)


# ── Config ────────────────────────────────────────────────────────────────────

@dataclass
class RefactoringConfig(Config):
    min_depth: int = 6
    max_depth: int = 10
    timeout: float = 3.0

    def update(self, c):
        self.min_depth += int(c)
        self.max_depth += 2 * int(c)


# ── Scoring helper (self-free) ────────────────────────────────────────────────

def _normalize_label(s: str) -> str:
    return str(s).strip().lower().replace(' ', '_')


# ── Task ──────────────────────────────────────────────────────────────────────

class Refactoring(Task):
    task_name = "refactoring"
    balancing_key_ratio = 0.3   # 4 labels; 0.3 allows ~1-2 per label in batches of 4

    def __init__(self, config=None):
        super().__init__(
            config=config if config is not None else RefactoringConfig()
        )
        self._fuzzer = Fuzzer(
            grammar_fn=pygram_grammar,
            min_depth=self.config.min_depth,
            max_depth=self.config.max_depth,
        )
        self._triviality = TrivialityFilter(PYGRAM_TRIVIALITY_POLICY)

    def _refresh_fuzzer(self):
        if (self._fuzzer.min_depth != self.config.min_depth
                or self._fuzzer.max_depth != self.config.max_depth):
            self._fuzzer = Fuzzer(
                grammar_fn=pygram_grammar,
                min_depth=self.config.min_depth,
                max_depth=self.config.max_depth,
            )

    def _run_with_call(self, code: str, rng: random.Random, rng_state):
        """Execute `code` with a deterministically-wrapped entry call.

        Returns (success, stdout_stripped). Uses `rng_state` so the original
        and transformed programs receive identical entry-call arguments.
        """
        rng.setstate(rng_state)
        prepared, _name, _args = add_entry_call(code, rng)
        result = run_sandboxed(prepared, timeout=self.config.timeout)
        if not result.success:
            return False, '', prepared
        return True, result.stdout.strip(), prepared

    # ── Generation ────────────────────────────────────────────────────────

    def generate(self) -> Problem:
        self._refresh_fuzzer()
        rng = random.Random()
        engine = _TransformationEngine(rng)

        for _ in range(80):
            try:
                node = self._fuzzer.sample(1, seed=rng.randint(0, 2**31))[0]
                clean = node @ 'py'
            except Exception:
                continue

            if self._triviality.is_trivial(clean):
                continue

            # Use a fixed sub-rng for entry-call args, so original and
            # transformed programs get the same arguments.
            call_rng = random.Random(rng.randint(0, 2**31))
            call_state = call_rng.getstate()

            ok, clean_output, clean_prepared = self._run_with_call(
                clean, call_rng, call_state
            )
            if not ok or not clean_output:
                continue

            # Pick a transformation strategy and apply it
            strategies = TRANSFORMATIONS.copy()
            rng.shuffle(strategies)
            transformed = None
            strategy = None
            for candidate in strategies:
                t = engine.transform_with_strategy(clean, candidate)
                if t is not None and t != clean:
                    transformed = t
                    strategy = candidate
                    break
            if strategy is None:
                continue

            # Verify equivalence with the same call arguments
            ok_t, transformed_output, transformed_prepared = self._run_with_call(
                transformed, call_rng, call_state
            )
            if not ok_t or transformed_output != clean_output:
                continue

            metrics = ASTMetrics.from_code(clean)
            lines_changed = _count_changed_lines(clean, transformed)

            metadata = edict(
                original_code=clean_prepared,
                transformed_code=transformed_prepared,
                shared_output=clean_output,
                label=strategy,
                choices=list(TRANSFORMATIONS),
                original_num_lines=len(clean_prepared.splitlines()),
                transformed_num_lines=len(transformed_prepared.splitlines()),
                lines_changed=lines_changed,
                grammar='pygram',
                metrics=metrics.to_dict(),
            )
            return Problem(metadata=metadata, answer=strategy)

        raise RuntimeError("Refactoring: failed after 80 attempts")

    # ── Prompt ────────────────────────────────────────────────────────────

    def prompt(self, metadata) -> str:
        choices_text = '\n'.join(f"  - {c}" for c in metadata.choices)
        return (
            f"Below are two Python programs. They produce the same output "
            f"when executed. Program B was derived from Program A by "
            f"applying exactly one of the following AST-level "
            f"transformations:\n\n"
            f"{choices_text}\n\n"
            f"Program A:\n"
            f"```python\n{metadata.original_code}\n```\n\n"
            f"Program B:\n"
            f"```python\n{metadata.transformed_code}\n```\n\n"
            f"Which transformation was applied? Answer with the exact name "
            f"of the transformation (e.g. `variable_inlining`)."
        )

    # ── Scoring (self-free) ───────────────────────────────────────────────

    def score_answer(self, answer, entry):
        if answer is None:
            return 0
        a = _normalize_label(answer)
        r = _normalize_label(entry['answer'])
        if a == r:
            return 1
        return 0

    # ── Balancing ─────────────────────────────────────────────────────────

    def balancing_key(self, problem):
        return str(problem.answer)
