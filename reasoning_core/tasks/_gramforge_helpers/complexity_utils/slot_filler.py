"""
slot_filler.py
==============
Generates type- and scope-constrained expressions to fill template slots.

Design goals
------------
- Side-effect-free:     no calls, no comprehensions, no attribute access.
- Scope-respecting:     only references variables declared in scope.
- Type-consistent:      produces the declared slot type.
- Complexity-safe:      generated expressions are O(1) so they cannot alter
                        the host template's complexity class.
- Magnitude-safe:       for accumulator-update slots, avoids multiplication
                        so accumulated values grow only linearly in #ops.
                        Prevents catastrophic integer blowup that makes
                        wall-clock time explode even when op-count stays flat.

Slot purposes
-------------
    'init'         — initializer; biased toward literals / simple leaves
    'body'         — general body expression; full operator set
    'result'       — final return value; full operator set but shallow
    'accum_update' — RHS of `acc = <slot>` inside a loop; additive only
                     (the *critical* purpose for complexity-safe O(n^2)+)
"""

import random
from typing import Optional

from .complexity_templates import SlotSpec, Template


# ── Literal pools ─────────────────────────────────────────────────────────────

_INT_LITERALS = [0, 1, 2, 3, 5, 7, 10]

# For general body / result / init expressions: full commutative int ops
_BINOPS_INT_FULL     = ['+', '-', '*']
# For accumulator updates: additive only, so acc grows at most linearly per iter
_BINOPS_INT_ADDITIVE = ['+', '-']

_CMPOPS              = ['<', '<=', '>', '>=', '==', '!=']


# ── Filler ────────────────────────────────────────────────────────────────────

class SlotFiller:
    """
    Generates expressions for template slots.

    Parameters
    ----------
    rng : random.Random or int, optional
        RNG or seed. If None, uses a fresh Random().
    max_int_depth : int
        Maximum recursion depth for integer expressions. Depth 2 gives
        reasonably rich expressions without getting unreadable.
    """

    def __init__(self, rng=None, max_int_depth: int = 2):
        if isinstance(rng, int):
            self.rng = random.Random(rng)
        elif rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.max_int_depth = max_int_depth

    # ── Public API ────────────────────────────────────────────────────────

    def fill(self, spec: SlotSpec) -> str:
        if spec.type == 'int':
            return self._gen_int(spec.scope, depth=self.max_int_depth,
                                 purpose=spec.purpose)
        if spec.type == 'bool':
            return self._gen_bool(spec.scope)
        raise ValueError(f"Unsupported slot type: {spec.type!r}")

    def fill_template(self, tpl: Template) -> dict:
        return {name: self.fill(spec) for name, spec in tpl.slots.items()}

    # ── Internals: integer expressions ────────────────────────────────────

    def _op_set(self, purpose: str) -> list:
        """Select the operator set based on slot purpose."""
        if purpose == 'accum_update':
            return _BINOPS_INT_ADDITIVE
        return _BINOPS_INT_FULL

    def _gen_int(self, scope: list, depth: int, purpose: str = 'body') -> str:
        """
        Generate an integer-valued expression.

        Strategy:
          depth 0 → leaf (literal or variable)
          depth >0 → binop(leaf_or_subexpr, leaf_or_subexpr)

        Accumulator-update slots are depth-limited to 1 and use only
        additive operators, to keep running values from exploding in
        magnitude inside loops.
        """
        ops = self._op_set(purpose)

        # accum_update slots cap depth at 1 (one binop, leaves below)
        if purpose == 'accum_update':
            depth = min(depth, 1)

        # init slots bias toward simple literals/vars
        if purpose == 'init' and self.rng.random() < 0.5:
            return self._int_leaf(scope)

        if depth <= 0:
            return self._int_leaf(scope)

        # 60% compound, 40% leaf for variety
        if self.rng.random() < 0.4:
            return self._int_leaf(scope)

        op = self.rng.choice(ops)
        left  = self._gen_int(scope, depth - 1, purpose='body')
        right = self._gen_int(scope, depth - 1, purpose='body')
        return f"({left} {op} {right})"

    def _int_leaf(self, scope: list) -> str:
        vars_in_scope = [v for v in scope if v is not None]
        if vars_in_scope and self.rng.random() < 0.65:
            return self.rng.choice(vars_in_scope)
        return str(self.rng.choice(_INT_LITERALS))

    # ── Internals: boolean expressions ────────────────────────────────────

    def _gen_bool(self, scope: list) -> str:
        op = self.rng.choice(_CMPOPS)
        left  = self._gen_int(scope, depth=1, purpose='body')
        right = self._gen_int(scope, depth=1, purpose='body')
        return f"{left} {op} {right}"
