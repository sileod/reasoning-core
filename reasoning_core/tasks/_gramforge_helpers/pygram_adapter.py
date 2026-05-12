"""
_gramforge_helpers/pygram_adapter.py
====================================
Wraps pygram-generated function definitions with entry-point calls so they
become runnable scripts. Used by runnability, output_prediction, and
refactoring tasks.

Verbatim port from gramforge/tasks/pygram_adapter.py.
"""

import ast
import random
import textwrap
from typing import Optional

from .prerequisites import TrivialityPolicy


def sample_argument(type_name: str, rng: random.Random) -> str:
    t = type_name.strip().lower()
    base = t.split('[')[0].strip()
    if base == 'int':
        return str(rng.randint(1, 10))
    if base == 'float':
        return f'{rng.uniform(1.0, 10.0):.2f}'
    if base == 'bool':
        return rng.choice(['True', 'False'])
    if base == 'str':
        return repr(rng.choice(['hi', 'ab', 'xyz', 'code', 'test']))
    if base == 'list':
        length = rng.randint(2, 5)
        return '[' + ', '.join(str(rng.randint(0, 10)) for _ in range(length)) + ']'
    if base == 'dict':
        return '{}'
    if base == 'tuple':
        return '(1, 2, 3)'
    if base == 'none':
        return 'None'
    return str(rng.randint(1, 10))


def _type_hint_name(annotation: Optional[ast.AST]) -> str:
    if annotation is None:
        return 'int'
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Subscript):
        if isinstance(annotation.value, ast.Name):
            name = annotation.value.id
            if name == 'Optional' and isinstance(annotation.slice, ast.Name):
                return annotation.slice.id
            return name
    return 'int'


def _score_cross_calls(fn: ast.FunctionDef, defined_names: set) -> int:
    count = 0
    for node in ast.walk(fn):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name in defined_names and name != fn.name:
                count += 1
    return count


def _select_entry_function(tree: ast.Module, strategy: str):
    funcs = [stmt for stmt in tree.body
             if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if not funcs:
        return None
    if strategy == 'first':
        return funcs[0]
    if strategy == 'best_cross_call':
        defined_names = {f.name for f in funcs}
        scored = [(f, _score_cross_calls(f, defined_names), idx)
                  for idx, f in enumerate(funcs)]
        scored.sort(key=lambda t: (-t[1], t[2]))
        return scored[0][0]
    raise ValueError(f"Unknown entry strategy: {strategy!r}")


def add_entry_call(code: str, rng: Optional[random.Random] = None,
                   strategy: str = 'first') -> tuple:
    if rng is None:
        rng = random.Random()
    try:
        tree = ast.parse(textwrap.dedent(code))
    except SyntaxError:
        return code, None, []
    entry = _select_entry_function(tree, strategy)
    if entry is None:
        return code, None, []
    arg_sources: list = []
    arg_values: list = []
    for arg in entry.args.args:
        type_name = _type_hint_name(arg.annotation)
        src = sample_argument(type_name, rng)
        arg_sources.append(src)
        try:
            arg_values.append(eval(src, {'__builtins__': {}}))
        except Exception:
            arg_values.append(None)
    call_line = f"_result = {entry.name}({', '.join(arg_sources)})"
    wrapped = code.rstrip() + '\n\n' + call_line + '\n'
    return wrapped, entry.name, arg_values


def add_entry_call_str(code: str, rng: Optional[random.Random] = None,
                       strategy: str = 'first') -> str:
    wrapped, _, _ = add_entry_call(code, rng, strategy=strategy)
    return wrapped


PYGRAM_TRIVIALITY_POLICY = TrivialityPolicy(
    reject_empty=True,
    reject_single_assignment=True,
    reject_all_literal_prints=True,
    reject_identity_assignments=True,
    require_output=False,
    require_loops=False,
    require_top_level_execution=False,
)
