"""Typed, prompt-independent finite-domain CSP intermediate representation."""

from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from math import gcd
from typing import Any, Mapping, Sequence

import z3


@dataclass(frozen=True)
class Var:
    name: str
    domain: tuple[int, ...]
    sort: str = "int"

    def __init__(self, name: str, domain: Sequence[int], sort: str = "int"):
        values = tuple(sorted(set(domain)))
        if not values:
            raise ValueError("a variable domain cannot be empty")
        if sort not in {"int", "bool"}:
            raise ValueError(f"unsupported sort: {sort}")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "domain", values)
        object.__setattr__(self, "sort", sort)

    def canonical(self):
        return ("var", self.sort, self.name, self.domain)


class Formula:
    def to_z3(self, ctx: Mapping[str, z3.ArithRef]):
        raise NotImplementedError

    def canonical(self):
        raise NotImplementedError

    def variables(self) -> frozenset[Var]:
        raise NotImplementedError

    def complexity(self) -> int:
        return 1

    def render(self, renderer) -> str:
        return renderer.render(self)


def _vkey(v: Var):
    return v.canonical()


@dataclass(frozen=True)
class _VarValue(Formula):
    x: Var
    value: int

    def variables(self):
        return frozenset((self.x,))


@dataclass(frozen=True)
class Eq(_VarValue):
    def to_z3(self, ctx): return ctx[self.x.name] == self.value
    def canonical(self): return ("eq", _vkey(self.x), self.value)


@dataclass(frozen=True)
class Ne(_VarValue):
    def to_z3(self, ctx): return ctx[self.x.name] != self.value
    def canonical(self): return ("ne", _vkey(self.x), self.value)


@dataclass(frozen=True)
class In(Formula):
    x: Var
    values: tuple[int, ...]

    def __init__(self, x, values):
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "values", tuple(sorted(set(values))))

    def to_z3(self, ctx): return z3.Or(*[ctx[self.x.name] == v for v in self.values])
    def canonical(self): return ("in", _vkey(self.x), self.values)
    def variables(self): return frozenset((self.x,))


@dataclass(frozen=True)
class _VarVar(Formula):
    x: Var
    y: Var

    def variables(self): return frozenset((self.x, self.y))

    def _ordered(self):
        return tuple(sorted((_vkey(self.x), _vkey(self.y))))


@dataclass(frozen=True)
class EqVar(_VarVar):
    def to_z3(self, ctx): return ctx[self.x.name] == ctx[self.y.name]
    def canonical(self): return ("eqvar",) + self._ordered()


@dataclass(frozen=True)
class NeVar(_VarVar):
    def to_z3(self, ctx): return ctx[self.x.name] != ctx[self.y.name]
    def canonical(self): return ("nevar",) + self._ordered()


@dataclass(frozen=True)
class Lt(_VarVar):
    def to_z3(self, ctx): return ctx[self.x.name] < ctx[self.y.name]
    def canonical(self): return ("lt", _vkey(self.x), _vkey(self.y))


@dataclass(frozen=True)
class Distance(Formula):
    x: Var
    y: Var
    k: int

    def to_z3(self, ctx): return z3.Abs(ctx[self.x.name] - ctx[self.y.name]) == self.k
    def canonical(self): return ("distance",) + tuple(sorted((_vkey(self.x), _vkey(self.y)))) + (self.k,)
    def variables(self): return frozenset((self.x, self.y))


@dataclass(frozen=True)
class Linear(Formula):
    coeffs: tuple[int, ...]
    vars: tuple[Var, ...]
    op: str
    rhs: int

    def __init__(self, coeffs, vars, op, rhs):
        if len(coeffs) != len(vars) or not coeffs:
            raise ValueError("Linear needs equally sized non-empty coeffs and vars")
        if op not in {"==", "!=", "<=", ">="}:
            raise ValueError(f"unsupported linear operator: {op}")
        combined = {}
        for coefficient, var in zip(coeffs, vars):
            combined[var] = combined.get(var, 0) + int(coefficient)
        terms = sorted(((v, c) for v, c in combined.items() if c), key=lambda p: _vkey(p[0]))
        if not terms:
            raise ValueError("Linear cannot have all-zero coefficients")
        cs, vs = tuple(c for _, c in terms), tuple(v for v, _ in terms)
        divisor = reduce(gcd, (abs(c) for c in cs), 0)
        if divisor > 1 and rhs % divisor == 0:
            cs, rhs = tuple(c // divisor for c in cs), rhs // divisor
        if cs[0] < 0:
            cs, rhs = tuple(-c for c in cs), -rhs
            op = {"<=": ">=", ">=": "<="}.get(op, op)
        object.__setattr__(self, "coeffs", cs)
        object.__setattr__(self, "vars", vs)
        object.__setattr__(self, "op", op)
        object.__setattr__(self, "rhs", int(rhs))

    def _expr(self, ctx): return z3.Sum(*[a * ctx[v.name] for a, v in zip(self.coeffs, self.vars)])
    def to_z3(self, ctx):
        e = self._expr(ctx)
        return {"==": e == self.rhs, "!=": e != self.rhs, "<=": e <= self.rhs, ">=": e >= self.rhs}[self.op]
    def canonical(self): return ("linear", tuple(zip(self.coeffs, map(_vkey, self.vars))), self.op, self.rhs)
    def variables(self): return frozenset(self.vars)


@dataclass(frozen=True)
class Mod(Formula):
    expr: Linear
    modulus: int
    remainder: int

    def __init__(self, expr, modulus, remainder):
        if modulus < 2:
            raise ValueError("modulus must be at least 2")
        object.__setattr__(self, "expr", expr)
        object.__setattr__(self, "modulus", int(modulus))
        object.__setattr__(self, "remainder", int(remainder) % modulus)

    def to_z3(self, ctx): return self.expr._expr(ctx) % self.modulus == self.remainder
    def canonical(self):
        terms = tuple(zip(self.expr.coeffs, map(_vkey, self.expr.vars)))
        return ("mod", terms, self.modulus, self.remainder)
    def variables(self): return self.expr.variables()
    def complexity(self): return 1 + self.expr.complexity()


@dataclass(frozen=True)
class AllDifferent(Formula):
    vars: tuple[Var, ...]

    def __init__(self, vars): object.__setattr__(self, "vars", tuple(sorted(set(vars), key=_vkey)))
    def to_z3(self, ctx): return z3.Distinct(*[ctx[v.name] for v in self.vars])
    def canonical(self): return ("alldifferent", tuple(map(_vkey, self.vars)))
    def variables(self): return frozenset(self.vars)


@dataclass(frozen=True)
class Not(Formula):
    formula: Formula
    def to_z3(self, ctx): return z3.Not(self.formula.to_z3(ctx))
    def canonical(self): return ("not", self.formula.canonical())
    def variables(self): return self.formula.variables()
    def complexity(self): return 1 + self.formula.complexity()


class _Many(Formula):
    tag = "many"

    def __init__(self, formulas):
        flat = []
        for formula in formulas:
            flat.extend(formula.formulas if isinstance(formula, type(self)) else (formula,))
        unique = {f.canonical(): f for f in flat}
        object.__setattr__(self, "formulas", tuple(unique[k] for k in sorted(unique, key=repr)))

    def canonical(self): return (self.tag, tuple(f.canonical() for f in self.formulas))
    def variables(self): return frozenset().union(*(f.variables() for f in self.formulas))
    def complexity(self): return 1 + sum(f.complexity() for f in self.formulas)
    def __eq__(self, other): return type(self) is type(other) and self.canonical() == other.canonical()
    def __hash__(self): return hash(self.canonical())


class Or(_Many):
    tag = "or"
    def to_z3(self, ctx): return z3.Or(*[f.to_z3(ctx) for f in self.formulas])


class Xor(_Many):
    tag = "xor"
    def to_z3(self, ctx): return z3.PbEq([(f.to_z3(ctx), 1) for f in self.formulas], 1)


@dataclass(frozen=True)
class Implies(Formula):
    a: Formula
    b: Formula
    def to_z3(self, ctx): return z3.Implies(self.a.to_z3(ctx), self.b.to_z3(ctx))
    def canonical(self): return ("implies", self.a.canonical(), self.b.canonical())
    def variables(self): return self.a.variables() | self.b.variables()
    def complexity(self): return 1 + self.a.complexity() + self.b.complexity()


@dataclass(frozen=True)
class _Cardinality(Formula):
    k: int
    formulas: tuple[Formula, ...]
    tag = "cardinality"

    def __init__(self, k, formulas):
        fs = tuple(sorted(formulas, key=lambda f: repr(f.canonical())))
        object.__setattr__(self, "k", int(k)); object.__setattr__(self, "formulas", fs)
    def canonical(self): return (self.tag, self.k, tuple(f.canonical() for f in self.formulas))
    def variables(self): return frozenset().union(*(f.variables() for f in self.formulas))
    def complexity(self): return 1 + sum(f.complexity() for f in self.formulas)


class Exactly(_Cardinality):
    tag = "exactly"
    def to_z3(self, ctx): return z3.PbEq([(f.to_z3(ctx), 1) for f in self.formulas], self.k)


class AtMost(_Cardinality):
    tag = "atmost"
    def to_z3(self, ctx): return z3.PbLe([(f.to_z3(ctx), 1) for f in self.formulas], self.k)


def canonical_unique(formulas):
    """Deduplicate formulas by normalized semantic structure."""
    return list({f.canonical(): f for f in formulas}.values())


def operator_name(formula: Formula) -> str:
    return formula.canonical()[0]
