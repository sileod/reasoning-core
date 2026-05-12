"""
complexity_templates.py
=======================
Slot-filled templates for complexity classification.

See slot_filler.py for slot-purpose semantics. In particular:
slots marked purpose='accum_update' are those that update an accumulator
variable inside a loop. The slot filler restricts such slots to additive
operators (no multiplication) so that iterated updates keep magnitude
bounded — preventing wall-clock blowup on O(n^2) and O(n log n) templates
even though op-count stays on-curve.
"""

import ast
import re
import textwrap
from dataclasses import dataclass, field
from typing import Callable


LABELS = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)']


@dataclass
class SlotSpec:
    type: str = 'int'
    scope: list = field(default_factory=list)
    purpose: str = 'body'


@dataclass
class Template:
    name: str
    label: str
    skeleton: str
    slots: dict
    entry: str = 'solve'

    def slot_names(self) -> list:
        return re.findall(r'\{\{(\w+)\}\}', self.skeleton)

    def instantiate(self, fills: dict) -> str:
        missing = set(self.slots) - set(fills)
        if missing:
            raise ValueError(f"Template {self.name}: unfilled slots {missing}")
        extra = set(fills) - set(self.slots)
        if extra:
            raise ValueError(f"Template {self.name}: unknown slots {extra}")
        result = self.skeleton
        for slot_name, expr in fills.items():
            result = result.replace('{{' + slot_name + '}}', expr)
        return textwrap.dedent(result)


_DUMMY_FILLS = {
    'int':  '0',
    'str':  "''",
    'bool': 'False',
}


def _validate_template(tpl: Template) -> None:
    declared = set(tpl.slots)
    in_skeleton = set(tpl.slot_names())
    if declared != in_skeleton:
        raise ValueError(
            f"Template {tpl.name}: declared slots {declared} "
            f"≠ skeleton slots {in_skeleton}"
        )
    dummy_fills = {
        name: _DUMMY_FILLS.get(spec.type, '0')
        for name, spec in tpl.slots.items()
    }
    code = tpl.instantiate(dummy_fills)
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"Template {tpl.name}: dummy instantiation invalid: {e}")
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == tpl.entry:
            args = node.args.args
            if len(args) != 1 or args[0].arg != 'n':
                raise ValueError(
                    f"Template {tpl.name}: entry `{tpl.entry}` must take (n)"
                )
            return
    raise ValueError(
        f"Template {tpl.name}: no entry function `{tpl.entry}` found"
    )


TEMPLATES: list[Template] = []


def _register(tpl: Template) -> Template:
    _validate_template(tpl)
    TEMPLATES.append(tpl)
    return tpl


# =============================================================================
# ── O(1) TEMPLATES (12) ──────────────────────────────────────────────────────
# =============================================================================

# ── Original O(1) (5) ─────────────────────────────────────────────────────────

_register(Template(
    name='const_arith',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{INIT_B}}
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_A': SlotSpec(type='int', scope=['n'], purpose='init'),
        'INIT_B': SlotSpec(type='int', scope=['n', 'a'], purpose='init'),
        'RESULT': SlotSpec(type='int', scope=['n', 'a', 'b'], purpose='result'),
    },
))

_register(Template(
    name='const_conditional',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            x = {{INIT}}
            if {{COND}}:
                r = {{BRANCH_A}}
            else:
                r = {{BRANCH_B}}
            return r
    ''').strip(),
    slots={
        'INIT':     SlotSpec(type='int',  scope=['n'],           purpose='init'),
        'COND':     SlotSpec(type='bool', scope=['n', 'x'],      purpose='body'),
        'BRANCH_A': SlotSpec(type='int',  scope=['n', 'x'],      purpose='body'),
        'BRANCH_B': SlotSpec(type='int',  scope=['n', 'x'],      purpose='body'),
    },
))

_register(Template(
    name='const_chain',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            p = {{INIT_P}}
            q = {{USE_P}}
            r = {{USE_Q}}
            return r
    ''').strip(),
    slots={
        'INIT_P': SlotSpec(type='int', scope=['n'],           purpose='init'),
        'USE_P':  SlotSpec(type='int', scope=['n', 'p'],      purpose='body'),
        'USE_Q':  SlotSpec(type='int', scope=['n', 'p', 'q'], purpose='body'),
    },
))

_register(Template(
    name='const_minmax',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{INIT_B}}
            if a > b:
                return {{RESULT_A}}
            return {{RESULT_B}}
    ''').strip(),
    slots={
        'INIT_A':   SlotSpec(type='int', scope=['n'],           purpose='init'),
        'INIT_B':   SlotSpec(type='int', scope=['n', 'a'],      purpose='init'),
        'RESULT_A': SlotSpec(type='int', scope=['n', 'a', 'b'], purpose='result'),
        'RESULT_B': SlotSpec(type='int', scope=['n', 'a', 'b'], purpose='result'),
    },
))

_register(Template(
    name='const_nested_if',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            v = {{INIT}}
            if {{OUTER_COND}}:
                if {{INNER_COND}}:
                    v = {{INNER_BODY}}
                else:
                    v = {{ELSE_BODY}}
            return v
    ''').strip(),
    slots={
        'INIT':       SlotSpec(type='int',  scope=['n'],      purpose='init'),
        'OUTER_COND': SlotSpec(type='bool', scope=['n', 'v'], purpose='body'),
        'INNER_COND': SlotSpec(type='bool', scope=['n', 'v'], purpose='body'),
        'INNER_BODY': SlotSpec(type='int',  scope=['n', 'v'], purpose='body'),
        'ELSE_BODY':  SlotSpec(type='int',  scope=['n', 'v'], purpose='body'),
    },
))


# ── Batch 2 kept (4): early-return, elif chain, three-var chain, precompute ─

# Early-return on a single condition — no loop, O(1).
_register(Template(
    name='const_early_return',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            x = {{INIT}}
            if {{COND}}:
                return {{EARLY}}
            return {{DEFAULT}}
    ''').strip(),
    slots={
        'INIT':    SlotSpec(type='int',  scope=['n'],      purpose='init'),
        'COND':    SlotSpec(type='bool', scope=['n', 'x'], purpose='body'),
        'EARLY':   SlotSpec(type='int',  scope=['n', 'x'], purpose='result'),
        'DEFAULT': SlotSpec(type='int',  scope=['n', 'x'], purpose='result'),
    },
))

# Three-branch elif chain — still O(1), tests longer branching paths.
_register(Template(
    name='const_elif_chain',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            x = {{INIT}}
            if {{COND_A}}:
                r = {{BRANCH_A}}
            elif {{COND_B}}:
                r = {{BRANCH_B}}
            else:
                r = {{BRANCH_C}}
            return r
    ''').strip(),
    slots={
        'INIT':     SlotSpec(type='int',  scope=['n'],      purpose='init'),
        'COND_A':   SlotSpec(type='bool', scope=['n', 'x'], purpose='body'),
        'BRANCH_A': SlotSpec(type='int',  scope=['n', 'x'], purpose='body'),
        'COND_B':   SlotSpec(type='bool', scope=['n', 'x'], purpose='body'),
        'BRANCH_B': SlotSpec(type='int',  scope=['n', 'x'], purpose='body'),
        'BRANCH_C': SlotSpec(type='int',  scope=['n', 'x'], purpose='body'),
    },
))

# Three variables in a dependency chain, no loops.
_register(Template(
    name='const_three_var_chain',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{USE_A}}
            c = {{USE_B}}
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_A': SlotSpec(type='int', scope=['n'],                purpose='init'),
        'USE_A':  SlotSpec(type='int', scope=['n', 'a'],           purpose='body'),
        'USE_B':  SlotSpec(type='int', scope=['n', 'a', 'b'],      purpose='body'),
        'RESULT': SlotSpec(type='int', scope=['n', 'a', 'b', 'c'], purpose='result'),
    },
))

# Nested conditional with a computation before branching.
_register(Template(
    name='const_precompute_branch',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            p = {{INIT_P}}
            q = {{USE_P}}
            if {{COND}}:
                return {{BRANCH_A}}
            return {{BRANCH_B}}
    ''').strip(),
    slots={
        'INIT_P':   SlotSpec(type='int',  scope=['n'],           purpose='init'),
        'USE_P':    SlotSpec(type='int',  scope=['n', 'p'],      purpose='body'),
        'COND':     SlotSpec(type='bool', scope=['n', 'p', 'q'], purpose='body'),
        'BRANCH_A': SlotSpec(type='int',  scope=['n', 'p', 'q'], purpose='result'),
        'BRANCH_B': SlotSpec(type='int',  scope=['n', 'p', 'q'], purpose='result'),
    },
))


# ── Batch 3 new (3): clamp, inline conditional, three-way compare ─────────────

# Clamp pattern: bounded value via min/max-style if-chain.
_register(Template(
    name='const_clamp',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            x = {{INIT}}
            lo = {{LO}}
            hi = {{HI}}
            if x < lo:
                x = lo
            if x > hi:
                x = hi
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT':   SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'LO':     SlotSpec(type='int', scope=['n', 'x'],             purpose='init'),
        'HI':     SlotSpec(type='int', scope=['n', 'x', 'lo'],       purpose='init'),
        'RESULT': SlotSpec(type='int', scope=['n', 'x', 'lo', 'hi'], purpose='result'),
    },
))

# Ternary-style expression: inline conditional in a single expression.
_register(Template(
    name='const_inline_conditional',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{INIT_B}}
            return {{BRANCH_A}} if {{COND}} else {{BRANCH_B}}
    ''').strip(),
    slots={
        'INIT_A':   SlotSpec(type='int',  scope=['n'],           purpose='init'),
        'INIT_B':   SlotSpec(type='int',  scope=['n', 'a'],      purpose='init'),
        'COND':     SlotSpec(type='bool', scope=['n', 'a', 'b'], purpose='body'),
        'BRANCH_A': SlotSpec(type='int',  scope=['n', 'a', 'b'], purpose='result'),
        'BRANCH_B': SlotSpec(type='int',  scope=['n', 'a', 'b'], purpose='result'),
    },
))

# Three-way comparison result.
_register(Template(
    name='const_three_way_compare',
    label='O(1)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{INIT_B}}
            if a < b:
                return {{LESS}}
            if a > b:
                return {{MORE}}
            return {{EQUAL}}
    ''').strip(),
    slots={
        'INIT_A': SlotSpec(type='int', scope=['n'],           purpose='init'),
        'INIT_B': SlotSpec(type='int', scope=['n', 'a'],      purpose='init'),
        'LESS':   SlotSpec(type='int', scope=['n', 'a', 'b'], purpose='result'),
        'MORE':   SlotSpec(type='int', scope=['n', 'a', 'b'], purpose='result'),
        'EQUAL':  SlotSpec(type='int', scope=['n', 'a', 'b'], purpose='result'),
    },
))


# =============================================================================
# ── O(log n) TEMPLATES (12) ───────────────────────────────────────────────────
# =============================================================================

# ── Original O(log n) (5) ─────────────────────────────────────────────────────

_register(Template(
    name='log_halving',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 1:
                acc = {{BODY}}
                k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                 purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'k', 'acc'],     purpose='accum_update'),
    },
))

_register(Template(
    name='log_doubling',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = 1
            while k < n:
                acc = {{BODY}}
                k = k * 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],               purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'k', 'acc'],   purpose='accum_update'),
    },
))

_register(Template(
    name='log_halving_conditional',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 1:
                if {{COND}}:
                    acc = {{BODY_A}}
                else:
                    acc = {{BODY_B}}
                k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT':   SlotSpec(type='int',  scope=['n'],                purpose='init'),
        'COND':   SlotSpec(type='bool', scope=['n', 'k', 'acc'],    purpose='body'),
        'BODY_A': SlotSpec(type='int',  scope=['n', 'k', 'acc'],    purpose='accum_update'),
        'BODY_B': SlotSpec(type='int',  scope=['n', 'k', 'acc'],    purpose='accum_update'),
    },
))

_register(Template(
    name='log_halving_after_init',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            base = {{BASE}}
            acc = base
            k = n
            while k > 1:
                acc = {{BODY}}
                k = k // 2
            return acc
    ''').strip(),
    slots={
        'BASE': SlotSpec(type='int', scope=['n'],                       purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'k', 'base', 'acc'],   purpose='accum_update'),
    },
))

_register(Template(
    name='log_two_vars_halving',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            x = {{INIT_X}}
            y = {{INIT_Y}}
            k = n
            while k > 1:
                x = {{UPDATE_X}}
                y = {{UPDATE_Y}}
                k = k // 2
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_X':   SlotSpec(type='int', scope=['n'],                      purpose='init'),
        'INIT_Y':   SlotSpec(type='int', scope=['n', 'x'],                 purpose='init'),
        'UPDATE_X': SlotSpec(type='int', scope=['n', 'k', 'x', 'y'],       purpose='accum_update'),
        'UPDATE_Y': SlotSpec(type='int', scope=['n', 'k', 'x', 'y'],       purpose='accum_update'),
        'RESULT':   SlotSpec(type='int', scope=['n', 'x', 'y'],            purpose='result'),
    },
))


# ── Batch 2 kept (5): thirding, two sequential, guarded doubling,
#                     step counter, halving inner branch ──────────────────────

# Step by thirds (k //= 3) — O(log₃ n) = O(log n).
_register(Template(
    name='log_thirding',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 1:
                acc = {{BODY}}
                k = k // 3
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],               purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'k', 'acc'],   purpose='accum_update'),
    },
))

# Two sequential (non-nested) log loops — still O(log n).
_register(Template(
    name='log_two_sequential_loops',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            k = n
            while k > 1:
                a = {{BODY_A}}
                k = k // 2
            b = {{INIT_B}}
            k = n
            while k > 1:
                b = {{BODY_B}}
                k = k // 2
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_A': SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY_A': SlotSpec(type='int', scope=['n', 'k', 'a'],        purpose='accum_update'),
        'INIT_B': SlotSpec(type='int', scope=['n', 'a'],             purpose='init'),
        'BODY_B': SlotSpec(type='int', scope=['n', 'k', 'b'],        purpose='accum_update'),
        'RESULT': SlotSpec(type='int', scope=['n', 'a', 'b'],        purpose='result'),
    },
))

# Doubling loop with an O(1) precompute guard before the loop.
_register(Template(
    name='log_guarded_doubling',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            base = {{BASE}}
            if {{GUARD}}:
                base = {{ALT}}
            acc = base
            k = 1
            while k < n:
                acc = {{BODY}}
                k = k * 2
            return acc
    ''').strip(),
    slots={
        'BASE':  SlotSpec(type='int',  scope=['n'],                        purpose='init'),
        'GUARD': SlotSpec(type='bool', scope=['n', 'base'],                purpose='body'),
        'ALT':   SlotSpec(type='int',  scope=['n', 'base'],                purpose='init'),
        'BODY':  SlotSpec(type='int',  scope=['n', 'k', 'base', 'acc'],    purpose='accum_update'),
    },
))

# Halving loop that tracks the step count explicitly.
_register(Template(
    name='log_step_counter',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            steps = 0
            k = n
            while k > 1:
                acc = {{BODY}}
                steps = steps + 1
                k = k // 2
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT':   SlotSpec(type='int', scope=['n'],                        purpose='init'),
        'BODY':   SlotSpec(type='int', scope=['n', 'k', 'steps', 'acc'],   purpose='accum_update'),
        'RESULT': SlotSpec(type='int', scope=['n', 'steps', 'acc'],        purpose='result'),
    },
))

# Halving loop with an inner O(1) conditional that doesn't add a loop.
_register(Template(
    name='log_halving_inner_branch',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 1:
                x = {{INNER_INIT}}
                if {{INNER_COND}}:
                    acc = {{BODY_A}}
                else:
                    acc = {{BODY_B}}
                k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT':       SlotSpec(type='int',  scope=['n'],                        purpose='init'),
        'INNER_INIT': SlotSpec(type='int',  scope=['n', 'k', 'acc'],            purpose='init'),
        'INNER_COND': SlotSpec(type='bool', scope=['n', 'k', 'x', 'acc'],       purpose='body'),
        'BODY_A':     SlotSpec(type='int',  scope=['n', 'k', 'x', 'acc'],       purpose='accum_update'),
        'BODY_B':     SlotSpec(type='int',  scope=['n', 'k', 'x', 'acc'],       purpose='accum_update'),
    },
))


# ── Batch 3 new (2): fast-exp shape, base-10 digits ───────────────────────────

# Fast-exponentiation shape: iterates log₂(n) times via halving with bit-check.
_register(Template(
    name='log_fast_exp_shape',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 0:
                if k % 2 == 1:
                    acc = {{BODY_ODD}}
                else:
                    acc = {{BODY_EVEN}}
                k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT':      SlotSpec(type='int', scope=['n'],              purpose='init'),
        'BODY_ODD':  SlotSpec(type='int', scope=['n', 'k', 'acc'],  purpose='accum_update'),
        'BODY_EVEN': SlotSpec(type='int', scope=['n', 'k', 'acc'],  purpose='accum_update'),
    },
))

# Digit-counting style: while k > 0: k = k // 10. Still O(log n).
_register(Template(
    name='log_base10_digits',
    label='O(log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 0:
                acc = {{BODY}}
                k = k // 10
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],              purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'k', 'acc'],  purpose='accum_update'),
    },
))


# =============================================================================
# ── O(n) TEMPLATES (11) ───────────────────────────────────────────────────────
# =============================================================================

# ── Original O(n) (5) ─────────────────────────────────────────────────────────

_register(Template(
    name='linear_accumulator',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                 purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'acc'],     purpose='accum_update'),
    },
))

_register(Template(
    name='linear_conditional_accum',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                if {{COND}}:
                    acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int',  scope=['n'],              purpose='init'),
        'COND': SlotSpec(type='bool', scope=['n', 'i', 'acc'],  purpose='body'),
        'BODY': SlotSpec(type='int',  scope=['n', 'i', 'acc'],  purpose='accum_update'),
    },
))

_register(Template(
    name='linear_while',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            i = 0
            while i < n:
                acc = {{BODY}}
                i = i + 1
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],               purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'acc'],   purpose='accum_update'),
    },
))

_register(Template(
    name='linear_two_accumulators',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{INIT_B}}
            for i in range(n):
                a = {{UPDATE_A}}
                b = {{UPDATE_B}}
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_A':   SlotSpec(type='int', scope=['n'],                   purpose='init'),
        'INIT_B':   SlotSpec(type='int', scope=['n', 'a'],              purpose='init'),
        'UPDATE_A': SlotSpec(type='int', scope=['n', 'i', 'a', 'b'],    purpose='accum_update'),
        'UPDATE_B': SlotSpec(type='int', scope=['n', 'i', 'a', 'b'],    purpose='accum_update'),
        'RESULT':   SlotSpec(type='int', scope=['n', 'a', 'b'],         purpose='result'),
    },
))

_register(Template(
    name='linear_guarded_init',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            base = {{BASE}}
            if {{GUARD}}:
                base = {{ALT}}
            acc = base
            for i in range(n):
                acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'BASE':  SlotSpec(type='int',  scope=['n'],                        purpose='init'),
        'GUARD': SlotSpec(type='bool', scope=['n', 'base'],                purpose='body'),
        'ALT':   SlotSpec(type='int',  scope=['n', 'base'],                purpose='init'),
        'BODY':  SlotSpec(type='int',  scope=['n', 'i', 'base', 'acc'],    purpose='accum_update'),
    },
))


# ── Batch 2 kept (2): two sequential, inner precompute ────────────────────────

# Two sequential single loops — O(n) + O(n) = O(n).
_register(Template(
    name='linear_two_sequential_loops',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            for i in range(n):
                a = {{BODY_A}}
            b = {{INIT_B}}
            for i in range(n):
                b = {{BODY_B}}
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_A': SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY_A': SlotSpec(type='int', scope=['n', 'i', 'a'],        purpose='accum_update'),
        'INIT_B': SlotSpec(type='int', scope=['n', 'a'],             purpose='init'),
        'BODY_B': SlotSpec(type='int', scope=['n', 'i', 'b'],        purpose='accum_update'),
        'RESULT': SlotSpec(type='int', scope=['n', 'a', 'b'],        purpose='result'),
    },
))

# Linear loop with an O(1) inner precompute (not a nested loop).
_register(Template(
    name='linear_inner_precompute',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                tmp = {{TMP}}
                acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                    purpose='init'),
        'TMP':  SlotSpec(type='int', scope=['n', 'i', 'acc'],        purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'tmp', 'acc'], purpose='accum_update'),
    },
))


# ── Batch 3 new (4): early-exit dead, both-branches, dead-continue,
#                    inner-loop-dead-branch ──────────────────────────────────

# Early-exit linear loop with DEAD exit: worst-case O(n).
_register(Template(
    name='linear_early_exit_dead',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                if i > 1000000000:
                    break
                acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],              purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'acc'],  purpose='accum_update'),
    },
))

# Conditional accumulator with ELSE branch — both branches update acc.
_register(Template(
    name='linear_both_branches_update',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                if {{COND}}:
                    acc = {{BODY_IF}}
                else:
                    acc = {{BODY_ELSE}}
            return acc
    ''').strip(),
    slots={
        'INIT':      SlotSpec(type='int',  scope=['n'],              purpose='init'),
        'COND':      SlotSpec(type='bool', scope=['n', 'i', 'acc'],  purpose='body'),
        'BODY_IF':   SlotSpec(type='int',  scope=['n', 'i', 'acc'],  purpose='accum_update'),
        'BODY_ELSE': SlotSpec(type='int',  scope=['n', 'i', 'acc'],  purpose='accum_update'),
    },
))

# Continue-style skip with dead condition — still O(n).
_register(Template(
    name='linear_with_dead_continue',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                if i > 1000000000:
                    continue
                acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],              purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'acc'],  purpose='accum_update'),
    },
))

# Nested single loop inside a dead branch — stays O(n).
_register(Template(
    name='linear_inner_loop_dead_branch',
    label='O(n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                acc = {{BODY}}
                if i > 1000000000:
                    for j in range(n):
                        acc = {{DEAD_BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT':      SlotSpec(type='int', scope=['n'],                   purpose='init'),
        'BODY':      SlotSpec(type='int', scope=['n', 'i', 'acc'],       purpose='accum_update'),
        'DEAD_BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'],  purpose='accum_update'),
    },
))


# =============================================================================
# ── O(n log n) TEMPLATES (10) ─────────────────────────────────────────────────
# =============================================================================

# ── Original O(n log n) (5) ───────────────────────────────────────────────────

_register(Template(
    name='nlogn_outer_linear_inner_halving',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                k = n
                while k > 1:
                    acc = {{BODY}}
                    k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                         purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'k', 'acc'],        purpose='accum_update'),
    },
))

_register(Template(
    name='nlogn_outer_linear_inner_doubling',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                k = 1
                while k < n:
                    acc = {{BODY}}
                    k = k * 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                         purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'k', 'acc'],        purpose='accum_update'),
    },
))

_register(Template(
    name='nlogn_outer_halving_inner_linear',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 1:
                for i in range(n):
                    acc = {{BODY}}
                k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                         purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'k', 'acc'],        purpose='accum_update'),
    },
))

_register(Template(
    name='nlogn_conditional_inner',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                k = n
                while k > 1:
                    if {{COND}}:
                        acc = {{BODY}}
                    k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int',  scope=['n'],                        purpose='init'),
        'COND': SlotSpec(type='bool', scope=['n', 'i', 'k', 'acc'],       purpose='body'),
        'BODY': SlotSpec(type='int',  scope=['n', 'i', 'k', 'acc'],       purpose='accum_update'),
    },
))

_register(Template(
    name='nlogn_two_accumulators',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{INIT_B}}
            for i in range(n):
                k = n
                while k > 1:
                    a = {{UPDATE_A}}
                    b = {{UPDATE_B}}
                    k = k // 2
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_A':   SlotSpec(type='int', scope=['n'],                            purpose='init'),
        'INIT_B':   SlotSpec(type='int', scope=['n', 'a'],                       purpose='init'),
        'UPDATE_A': SlotSpec(type='int', scope=['n', 'i', 'k', 'a', 'b'],        purpose='accum_update'),
        'UPDATE_B': SlotSpec(type='int', scope=['n', 'i', 'k', 'a', 'b'],        purpose='accum_update'),
        'RESULT':   SlotSpec(type='int', scope=['n', 'a', 'b'],                  purpose='result'),
    },
))


# ── Batch 2 kept (2): outer doubling inner linear, outer thirding inner linear ─

# Outer doubling loop, inner linear loop — O(log n) * O(n) = O(n log n).
_register(Template(
    name='nlogn_outer_doubling_inner_linear',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = 1
            while k < n:
                for i in range(n):
                    acc = {{BODY}}
                k = k * 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'k', 'acc'], purpose='accum_update'),
    },
))

# Outer thirding loop, inner linear loop — O(log₃ n) * O(n) = O(n log n).
_register(Template(
    name='nlogn_outer_thirding_inner_linear',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 1:
                for i in range(n):
                    acc = {{BODY}}
                k = k // 3
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'k', 'acc'], purpose='accum_update'),
    },
))


# ── Batch 3 new (3): dead quadratic branch, log outer + precompute,
#                    linear outer + counter ──────────────────────────────────

# Dead inner n² loop inside a log outer — stays O(n log n) because branch dead.
_register(Template(
    name='nlogn_dead_quadratic_branch',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 1:
                for i in range(n):
                    acc = {{BODY}}
                if k > 1000000000:
                    for i in range(n):
                        for j in range(n):
                            acc = {{DEAD_BODY}}
                k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT':      SlotSpec(type='int', scope=['n'],                        purpose='init'),
        'BODY':      SlotSpec(type='int', scope=['n', 'i', 'k', 'acc'],       purpose='accum_update'),
        'DEAD_BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'k', 'acc'],  purpose='accum_update'),
    },
))

# Log outer with inner linear + inner precompute.
_register(Template(
    name='nlogn_log_outer_linear_precompute',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            k = n
            while k > 1:
                tmp = {{TMP}}
                for i in range(n):
                    acc = {{BODY}}
                k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                         purpose='init'),
        'TMP':  SlotSpec(type='int', scope=['n', 'k', 'acc'],             purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'k', 'tmp', 'acc'], purpose='accum_update'),
    },
))

# Linear outer, inner log with step-counter pattern.
_register(Template(
    name='nlogn_linear_outer_log_with_counter',
    label='O(n log n)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                k = n
                steps = 0
                while k > 1:
                    acc = {{BODY}}
                    steps = steps + 1
                    k = k // 2
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                                purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'k', 'steps', 'acc'],     purpose='accum_update'),
    },
))


# =============================================================================
# ── O(n^2) TEMPLATES (12) ─────────────────────────────────────────────────────
# =============================================================================

# ── Original O(n^2) (5) ───────────────────────────────────────────────────────

_register(Template(
    name='quadratic_nested',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                for j in range(n):
                    acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                         purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'],        purpose='accum_update'),
    },
))

_register(Template(
    name='quadratic_conditional',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                for j in range(n):
                    if {{COND}}:
                        acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int',  scope=['n'],                         purpose='init'),
        'COND': SlotSpec(type='bool', scope=['n', 'i', 'j', 'acc'],        purpose='body'),
        'BODY': SlotSpec(type='int',  scope=['n', 'i', 'j', 'acc'],        purpose='accum_update'),
    },
))

_register(Template(
    name='quadratic_while_outer',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            i = 0
            while i < n:
                for j in range(n):
                    acc = {{BODY}}
                i = i + 1
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                         purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'],        purpose='accum_update'),
    },
))

_register(Template(
    name='quadratic_with_inner_reset',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            total = {{INIT_TOTAL}}
            for i in range(n):
                inner = {{INIT_INNER}}
                for j in range(n):
                    inner = {{UPDATE_INNER}}
                total = {{UPDATE_TOTAL}}
            return total
    ''').strip(),
    slots={
        'INIT_TOTAL':   SlotSpec(type='int', scope=['n'],                          purpose='init'),
        'INIT_INNER':   SlotSpec(type='int', scope=['n', 'i', 'total'],            purpose='init'),
        'UPDATE_INNER': SlotSpec(type='int', scope=['n', 'i', 'j', 'inner'],       purpose='accum_update'),
        'UPDATE_TOTAL': SlotSpec(type='int', scope=['n', 'i', 'total', 'inner'],   purpose='accum_update'),
    },
))

_register(Template(
    name='quadratic_two_accumulators',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{INIT_B}}
            for i in range(n):
                for j in range(n):
                    a = {{UPDATE_A}}
                    b = {{UPDATE_B}}
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_A':   SlotSpec(type='int', scope=['n'],                         purpose='init'),
        'INIT_B':   SlotSpec(type='int', scope=['n', 'a'],                    purpose='init'),
        'UPDATE_A': SlotSpec(type='int', scope=['n', 'i', 'j', 'a', 'b'],     purpose='accum_update'),
        'UPDATE_B': SlotSpec(type='int', scope=['n', 'i', 'j', 'a', 'b'],     purpose='accum_update'),
        'RESULT':   SlotSpec(type='int', scope=['n', 'a', 'b'],               purpose='result'),
    },
))


# ── Batch 2 kept (2): triangular, inner precompute ────────────────────────────

# Triangular pattern — inner range(i) makes n*(n-1)/2 iterations = O(n^2).
_register(Template(
    name='quadratic_triangular',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                for j in range(i):
                    acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'], purpose='accum_update'),
    },
))

# Outer loop with an inner precompute then a full inner loop — O(n^2).
_register(Template(
    name='quadratic_inner_precompute',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                tmp = {{TMP}}
                for j in range(n):
                    acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                         purpose='init'),
        'TMP':  SlotSpec(type='int', scope=['n', 'i', 'acc'],             purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'tmp', 'acc'], purpose='accum_update'),
    },
))


# ── Batch 3 new (5): pair enumeration, dead inner break, double triangular,
#                    pair two accumulators, conditional always inner ─────────

# Pair-enumeration pattern: for j in range(i+1, n).
_register(Template(
    name='quadratic_pair_enumeration',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                for j in range(i + 1, n):
                    acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'], purpose='accum_update'),
    },
))

# Quadratic with dead break — worst-case O(n²), break never fires.
_register(Template(
    name='quadratic_dead_inner_break',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                for j in range(n):
                    if j > 1000000000:
                        break
                    acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'], purpose='accum_update'),
    },
))

# Double triangular: outer range(n), inner range(i), plus outer range(n)
# inner range(n-i). Both O(n²), summed = O(n²).
_register(Template(
    name='quadratic_double_triangular',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                for j in range(i):
                    acc = {{BODY_A}}
            for i in range(n):
                for j in range(n - i):
                    acc = {{BODY_B}}
            return acc
    ''').strip(),
    slots={
        'INIT':   SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY_A': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'], purpose='accum_update'),
        'BODY_B': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'], purpose='accum_update'),
    },
))

# Two-accumulator pair enumeration.
_register(Template(
    name='quadratic_pair_two_accumulators',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            a = {{INIT_A}}
            b = {{INIT_B}}
            for i in range(n):
                for j in range(i + 1, n):
                    a = {{UPDATE_A}}
                    b = {{UPDATE_B}}
            return {{RESULT}}
    ''').strip(),
    slots={
        'INIT_A':   SlotSpec(type='int', scope=['n'],                          purpose='init'),
        'INIT_B':   SlotSpec(type='int', scope=['n', 'a'],                     purpose='init'),
        'UPDATE_A': SlotSpec(type='int', scope=['n', 'i', 'j', 'a', 'b'],      purpose='accum_update'),
        'UPDATE_B': SlotSpec(type='int', scope=['n', 'i', 'j', 'a', 'b'],      purpose='accum_update'),
        'RESULT':   SlotSpec(type='int', scope=['n', 'a', 'b'],                purpose='result'),
    },
))

# Conditional inner loop with DEAD-NEGATIVE condition — always executes.
_register(Template(
    name='quadratic_conditional_always_inner',
    label='O(n^2)',
    skeleton=textwrap.dedent('''
        def solve(n: int) -> int:
            acc = {{INIT}}
            for i in range(n):
                if i < 1000000000:
                    for j in range(n):
                        acc = {{BODY}}
            return acc
    ''').strip(),
    slots={
        'INIT': SlotSpec(type='int', scope=['n'],                  purpose='init'),
        'BODY': SlotSpec(type='int', scope=['n', 'i', 'j', 'acc'], purpose='accum_update'),
    },
))


# ── Lookup helpers ────────────────────────────────────────────────────────────

def templates_by_label(label: str) -> list:
    return [t for t in TEMPLATES if t.label == label]


def get_template(name: str) -> Template:
    for t in TEMPLATES:
        if t.name == name:
            return t
    raise KeyError(f"No template named {name!r}")
