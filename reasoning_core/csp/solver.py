"""One Z3-backed solver interface for every CSP family."""

from __future__ import annotations

from itertools import product

import z3

from .ir import Eq, Formula, Not, Var


class CSPSolver:
    def __init__(self, variables, base=(), clues=()):
        self.variables = tuple(variables)
        if len({v.name for v in self.variables}) != len(self.variables):
            raise ValueError("variable names must be unique")
        self.base, self.clues = tuple(base), tuple(clues)
        self.ctx = {v.name: z3.Int(v.name) for v in self.variables}

    def solver(self, clues=None, extra=(), domains=None):
        solver = z3.Solver()
        for v in self.variables:
            values = v.domain if domains is None else domains[v]
            solver.add(z3.Or(*[self.ctx[v.name] == x for x in values]))
        for formula in (*self.base, *(self.clues if clues is None else clues), *extra):
            solver.add(formula.to_z3(self.ctx))
        return solver

    def is_sat(self, clues=None, extra=()):
        return self.solver(clues, extra).check() == z3.sat

    def possible_values(self, var, clues=None, extra=()):
        solver = self.solver(clues, extra)
        out = []
        for value in var.domain:
            solver.push(); solver.add(self.ctx[var.name] == value)
            if solver.check() == z3.sat: out.append(value)
            solver.pop()
        return out

    def unique_value(self, var, clues=None):
        values = self.possible_values(var, clues)
        return values[0] if len(values) == 1 else None

    def solutions(self, clues=None, limit=None):
        solver, out = self.solver(clues), []
        while solver.check() == z3.sat:
            model = solver.model()
            row = tuple(model.eval(self.ctx[v.name], model_completion=True).as_long() for v in self.variables)
            out.append(row)
            if limit is not None and len(out) > limit: return None, True
            solver.add(z3.Or(*[self.ctx[v.name] != x for v, x in zip(self.variables, row)]))
        return sorted(out), False

    def lex_solution(self, clues=None):
        optimizer = z3.Optimize(); optimizer.set(priority="lex")
        for assertion in self.solver(clues).assertions(): optimizer.add(assertion)
        for var in self.variables: optimizer.minimize(self.ctx[var.name])
        if optimizer.check() != z3.sat: return None
        model = optimizer.model()
        return tuple(model.eval(self.ctx[v.name], model_completion=True).as_long() for v in self.variables)

    def entails(self, formula, clues=None):
        return not self.is_sat(clues, (Not(formula),))

    def refutation_core(self, var, wrong_value, clues=None):
        active = list(self.clues if clues is None else clues)
        if self.is_sat(active, (Eq(var, wrong_value),)): return []
        for clue in list(active):
            trial = active.copy(); trial.remove(clue)
            if not self.is_sat(trial, (Eq(var, wrong_value),)): active = trial
        return active

    def full_unique(self, clues=None):
        solutions, overflow = self.solutions(clues, limit=1)
        return not overflow and len(solutions) == 1
