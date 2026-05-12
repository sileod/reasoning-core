# reasoning_core/tasks/runnability.py
"""
Runnability task.

Given a Python program (pygram-generated, wrapped with an entry-point call),
predict whether it executes to completion without raising an exception.

Labels: 'runnable' or 'error'.

Negative examples are either naturally-failing programs or valid programs
with an AST-level perturbation applied (undefined variable, wrong-type
argument, bad index, etc.).
"""

import ast
import itertools
import keyword
import random
import textwrap
from dataclasses import dataclass
from typing import Optional

from easydict import EasyDict as edict
from ._gramforge_helpers.grammars import pygram_grammar 

from reasoning_core.template import Task, Problem, Config

from ._gramforge_helpers.prerequisites import (
    Fuzzer, TrivialityFilter, run_sandboxed, ASTMetrics,
)
from ._gramforge_helpers.pygram_adapter import (
    add_entry_call_str, PYGRAM_TRIVIALITY_POLICY,
)


# ── Perturbation engine (AST-based, grammar-agnostic) ─────────────────────────

class _PerturbationEngine:
    """Applies AST-level perturbations to produce known-error programs."""

    STRATEGIES = [
        'undefined_variable',
        'wrong_type_in_range',
        'bad_list_index',
        'remove_first_init',
        'rename_function_call',
        'wrong_attribute_access',
        'force_zero_division',
        'inject_infinite_recursion',
    ]

    def __init__(self, rng: random.Random):
        self.rng = rng

    def perturb(self, code: str) -> tuple:
        """Apply a random perturbation. Returns (perturbed_code, strategy)."""
        strategies = self.STRATEGIES.copy()
        self.rng.shuffle(strategies)
        for strategy in strategies:
            try:
                result = getattr(self, f'_apply_{strategy}')(code)
            except SyntaxError:
                return code, 'none'
            if result is not None and result != code:
                return result, strategy
        return code, 'none'

    # -- helpers --

    @staticmethod
    def _parse(code: str) -> ast.Module:
        return ast.parse(textwrap.dedent(code))

    @staticmethod
    def _assigned_names(tree: ast.Module) -> list:
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.append(t.id)
        seen = set()
        ordered = []
        for n in names:
            if n not in seen:
                seen.add(n)
                ordered.append(n)
        return ordered

    @staticmethod
    def _all_names(tree: ast.Module) -> set:
        return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}

    def _fresh_name(self, existing: set) -> Optional[str]:
        reserved = set(keyword.kwlist) | {'True', 'False', 'None', 'print', 'range', 'len'}
        blocked = existing | reserved
        candidates = [c for c in 'abcdefghijklmnopqrstuvwxyz' if c not in blocked]
        if candidates:
            return self.rng.choice(candidates)
        for a, b in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=2):
            name = a + b
            if name not in blocked:
                return name
        return None

    def _typo_of(self, name: str, existing: set) -> Optional[str]:
        if len(name) == 0:
            return None
        reserved = set(keyword.kwlist) | {'True', 'False', 'None', 'print', 'range', 'len'}
        candidates: list = []
        for i, ch in enumerate(name):
            for repl in 'abcdefghijklmnopqrstuvwxyz':
                if repl != ch:
                    candidates.append(name[:i] + repl + name[i+1:])
        for i in range(len(name) - 1):
            if name[i] != name[i+1]:
                candidates.append(name[:i] + name[i+1] + name[i] + name[i+2:])
        if len(name) >= 2:
            for i in range(len(name)):
                candidates.append(name[:i] + name[i+1:])
        valid = [c for c in candidates
                 if c and c not in existing and c not in reserved and c.isidentifier()]
        if not valid:
            return None
        return self.rng.choice(valid)

    # -- strategies --

    def _apply_undefined_variable(self, code: str) -> Optional[str]:
        tree = self._parse(code)
        assigned = self._assigned_names(tree)
        if not assigned:
            return None
        load_uses = [n for n in ast.walk(tree)
                     if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
                     and n.id in assigned]
        if not load_uses:
            return None
        target = self.rng.choice(load_uses)
        all_names = self._all_names(tree)
        ghost = self._typo_of(target.id, all_names) or self._fresh_name(all_names)
        if ghost is None:
            return None
        target.id = ghost
        return ast.unparse(tree)

    def _apply_wrong_type_in_range(self, code: str) -> Optional[str]:
        tree = self._parse(code)
        range_args = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == 'range'):
                for idx, arg in enumerate(node.args):
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, int):
                        range_args.append((node, idx))
        if not range_args:
            return None
        call, idx = self.rng.choice(range_args)
        call.args[idx] = ast.Constant(value=self.rng.choice(['end', 'n', 'step']))
        return ast.unparse(tree)

    def _apply_bad_list_index(self, code: str) -> Optional[str]:
        tree = self._parse(code)
        list_vars = {}
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and isinstance(node.value, ast.List)):
                list_vars[node.targets[0].id] = len(node.value.elts)
        candidates = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Subscript):
                continue
            if not (isinstance(node.slice, ast.Constant)
                    and isinstance(node.slice.value, int)):
                continue
            if isinstance(node.value, ast.List):
                candidates.append((node, len(node.value.elts)))
            elif isinstance(node.value, ast.Name) and node.value.id in list_vars:
                candidates.append((node, list_vars[node.value.id]))
        if not candidates:
            return None
        sub, list_len = self.rng.choice(candidates)
        bad_idx = list_len + self.rng.randint(1, 3)
        sub.slice = ast.Constant(value=bad_idx)
        return ast.unparse(tree)

    def _apply_remove_first_init(self, code: str) -> Optional[str]:
        tree = self._parse(code)
        if not tree.body:
            return None
        first_idx = None
        first_name = None
        for i, stmt in enumerate(tree.body):
            if (isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)):
                first_idx = i
                first_name = stmt.targets[0].id
                break
        if first_idx is None:
            return None
        rest = ast.Module(body=tree.body[first_idx + 1:], type_ignores=[])
        used_after = any(
            isinstance(n, ast.Name) and n.id == first_name
            and isinstance(n.ctx, ast.Load)
            for n in ast.walk(rest)
        )
        if not used_after:
            return None
        tree.body = tree.body[:first_idx] + tree.body[first_idx + 1:]
        return ast.unparse(tree)

    def _apply_rename_function_call(self, code: str) -> Optional[str]:
        tree = self._parse(code)
        defined = {n.name for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        if not defined:
            return None
        call_sites = [n for n in ast.walk(tree)
                      if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Name)
                      and n.func.id in defined]
        if not call_sites:
            return None
        target = self.rng.choice(call_sites)
        all_names = self._all_names(tree) | defined | {'print', 'range', 'len'}
        ghost = self._typo_of(target.func.id, all_names) or self._fresh_name(all_names)
        if ghost is None:
            return None
        target.func.id = ghost
        return ast.unparse(tree)

    def _apply_wrong_attribute_access(self, code: str) -> Optional[str]:
        tree = self._parse(code)
        BAD_METHODS = {
            'list': ['upper', 'lower', 'split', 'capitalize'],
            'str':  ['append', 'pop', 'sort', 'extend'],
            'int':  ['upper', 'split', 'append', 'capitalize'],
        }
        typed_vars = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                val = node.value
                if isinstance(val, ast.List):
                    typed_vars[name] = 'list'
                elif isinstance(val, ast.Constant):
                    if isinstance(val.value, str):
                        typed_vars[name] = 'str'
                    elif isinstance(val.value, int) and not isinstance(val.value, bool):
                        typed_vars[name] = 'int'
        if not typed_vars:
            return None
        load_uses = [n for n in ast.walk(tree)
                     if isinstance(n, ast.Name)
                     and isinstance(n.ctx, ast.Load)
                     and n.id in typed_vars]
        if not load_uses:
            return None
        candidates = [(n, typed_vars[n.id]) for n in load_uses]
        target, var_type = self.rng.choice(candidates)
        method = self.rng.choice(BAD_METHODS[var_type])
        target_id = target.id
        target_method = method
        replaced = {'done': False}

        class _Replacer(ast.NodeTransformer):
            def visit_Name(self, node):
                if (not replaced['done']
                        and node.id == target_id
                        and isinstance(node.ctx, ast.Load)):
                    replaced['done'] = True
                    return ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id=target_id, ctx=ast.Load()),
                            attr=target_method, ctx=ast.Load()),
                        args=[], keywords=[],
                    )
                return node

        new_tree = _Replacer().visit(tree)
        if not replaced['done']:
            return None
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)

    def _apply_force_zero_division(self, code: str) -> Optional[str]:
        tree = self._parse(code)
        div_ops = (ast.Div, ast.FloorDiv, ast.Mod)
        mod_candidates = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.BinOp)
                    and isinstance(node.op, div_ops)
                    and isinstance(node.right, ast.Constant)
                    and isinstance(node.right.value, int)
                    and node.right.value != 0):
                mod_candidates.append(node)
        if mod_candidates:
            target = self.rng.choice(mod_candidates)
            target.right = ast.Constant(value=0)
            ast.fix_missing_locations(tree)
            return ast.unparse(tree)
        assigned = self._assigned_names(tree)
        if not assigned:
            return None
        var = assigned[0]
        inject = ast.parse(f'_zd = {var} / 0').body[0]
        ast.fix_missing_locations(inject)
        for i, stmt in enumerate(tree.body):
            if (isinstance(stmt, ast.Assign)
                    and len(stmt.targets) == 1
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id == var):
                tree.body.insert(i + 1, inject)
                ast.fix_missing_locations(tree)
                return ast.unparse(tree)
        return None

    def _apply_inject_infinite_recursion(self, code: str) -> Optional[str]:
        tree = self._parse(code)
        candidates = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            returns = [s for s in ast.walk(node) if isinstance(s, ast.Return)]
            if returns and node.args.args:
                candidates.append((node, returns))
        if not candidates:
            return None
        fn, returns = self.rng.choice(candidates)
        param_names = [a.arg for a in fn.args.args]
        self_call = ast.Call(
            func=ast.Name(id=fn.name, ctx=ast.Load()),
            args=[ast.Name(id=p, ctx=ast.Load()) for p in param_names],
            keywords=[],
        )
        new_return = ast.Return(value=self_call)
        target = returns[0]
        replaced = {'done': False}

        class _Replacer(ast.NodeTransformer):
            def visit_Return(self, node):
                if node is target and not replaced['done']:
                    replaced['done'] = True
                    return new_return
                return node

        new_tree = _Replacer().visit(tree)
        if not replaced['done']:
            return None
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)


# ── Config ────────────────────────────────────────────────────────────────────

@dataclass
class RunnabilityConfig(Config):
    min_depth: int = 6
    max_depth: int = 10
    timeout: float = 3.0

    def update(self, c):
        self.min_depth += int(c)
        self.max_depth += 2 * int(c)


# ── Scoring helper (must be self-free) ────────────────────────────────────────

def _normalize_label(s: str) -> str:
    return str(s).strip().lower()


# ── Task ──────────────────────────────────────────────────────────────────────

class Runnability(Task):
    task_name = "runnability"
    balancing_key_ratio = 0.5   # binary label

    def __init__(self, config=None):
        super().__init__(config=config if config is not None else RunnabilityConfig())
        self._fuzzer = Fuzzer(
            grammar_fn=pygram_grammar,
            min_depth=self.config.min_depth,
            max_depth=self.config.max_depth,
        )
        self._triviality = TrivialityFilter(PYGRAM_TRIVIALITY_POLICY)

    def _refresh_fuzzer(self):
        """Rebuild fuzzer if config depths changed (e.g., after set_level)."""
        if (self._fuzzer.min_depth != self.config.min_depth
                or self._fuzzer.max_depth != self.config.max_depth):
            self._fuzzer = Fuzzer(
                grammar_fn=pygram_grammar,
                min_depth=self.config.min_depth,
                max_depth=self.config.max_depth,
            )

    # ── Generation ────────────────────────────────────────────────────────

    def generate(self) -> Problem:
        self._refresh_fuzzer()
        rng = random.Random()
        engine = _PerturbationEngine(rng)

        # Decide whether to target a positive or a negative example on this attempt
        target_positive = rng.random() < 0.5

        for _ in range(80):
            try:
                node = self._fuzzer.sample(1, seed=rng.randint(0, 2**31))[0]
                raw_code = node @ 'py'
            except Exception:
                continue

            if self._triviality.is_trivial(raw_code):
                continue

            prepared = add_entry_call_str(raw_code, rng)
            result = run_sandboxed(prepared, timeout=self.config.timeout)

            if target_positive:
                if not result.success:
                    continue
                metrics = ASTMetrics.from_code(raw_code)
                metadata = edict(
                    code=prepared,
                    label='runnable',
                    error_type=None,
                    perturbation=None,
                    source='natural',
                    grammar='pygram',
                    metrics=metrics.to_dict(),
                    elapsed_ms=result.elapsed_ms,
                )
                return Problem(metadata=metadata, answer='runnable')

            # Targeting a negative example
            if not result.success:
                # Natural failure — accept directly
                metrics = ASTMetrics.from_code(raw_code)
                metadata = edict(
                    code=prepared,
                    label='error',
                    error_type=result.error_type,
                    perturbation=None,
                    source='natural',
                    grammar='pygram',
                    metrics=metrics.to_dict(),
                    elapsed_ms=result.elapsed_ms,
                )
                return Problem(metadata=metadata, answer='error')

            # Program runs — try perturbing it
            perturbed, strategy = engine.perturb(prepared)
            if strategy == 'none':
                continue
            p_result = run_sandboxed(perturbed, timeout=self.config.timeout)
            if p_result.success:
                continue   # perturbation didn't cause failure
            metrics = ASTMetrics.from_code(raw_code)
            metadata = edict(
                code=perturbed,
                label='error',
                error_type=p_result.error_type,
                perturbation=strategy,
                source='perturbed',
                grammar='pygram',
                metrics=metrics.to_dict(),
                elapsed_ms=p_result.elapsed_ms,
            )
            return Problem(metadata=metadata, answer='error')

        raise RuntimeError(
            f"Runnability: failed after 80 attempts (target={'+' if target_positive else '-'})"
        )

    # ── Prompt ────────────────────────────────────────────────────────────

    def prompt(self, metadata) -> str:
        return (
            f"Consider the following Python program. When it is executed, "
            f"does it run to completion without raising an exception, or does "
            f"it raise an error?\n\n"
            f"```python\n{metadata.code}\n```\n\n"
            f"Answer with exactly one of: `runnable` or `error`."
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
