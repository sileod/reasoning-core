"""Concise deterministic renderers, separate from CSP semantics."""

from .ir import (AllDifferent, AtMost, Distance, Eq, EqVar, Exactly, Implies,
                 In, Linear, Lt, Mod, Ne, NeVar, Not, Or, Xor)


class SymbolicRenderer:
    def name(self, var): return var.name

    def render(self, f):
        n = self.name
        if isinstance(f, Eq): return f"{n(f.x)} = {f.value}"
        if isinstance(f, Ne): return f"{n(f.x)} != {f.value}"
        if isinstance(f, EqVar): return f"{n(f.x)} = {n(f.y)}"
        if isinstance(f, NeVar): return f"{n(f.x)} != {n(f.y)}"
        if isinstance(f, Lt): return f"{n(f.x)} < {n(f.y)}"
        if isinstance(f, Distance): return f"|{n(f.x)} - {n(f.y)}| = {f.k}"
        if isinstance(f, In): return f"{n(f.x)} in {{{', '.join(map(str, f.values))}}}"
        if isinstance(f, AllDifferent): return f"AllDifferent({', '.join(n(v) for v in f.vars)})"
        if isinstance(f, Linear):
            terms = [n(v) if a == 1 else f"-{n(v)}" if a == -1 else f"{a}*{n(v)}" for a, v in zip(f.coeffs, f.vars)]
            return f"{' + '.join(terms).replace('+ -', '- ')} {f.op} {f.rhs}"
        if isinstance(f, Mod): return f"({self.render(f.expr).rsplit(' ', 2)[0]}) % {f.modulus} = {f.remainder}"
        if isinstance(f, Not): return f"not ({self.render(f.formula)})"
        if isinstance(f, Implies): return f"if {self.render(f.a)}, then {self.render(f.b)}"
        if isinstance(f, (Or, Xor)):
            join = " or " if isinstance(f, Or) else " xor "
            return join.join(f"({self.render(x)})" for x in f.formulas)
        if isinstance(f, (Exactly, AtMost)):
            label = "Exactly" if isinstance(f, Exactly) else "At most"
            return f"{label} {f.k} of [{'; '.join(self.render(x) for x in f.formulas)}]"
        raise TypeError(type(f).__name__)


class AssignmentRenderer(SymbolicRenderer):
    def __init__(self, labels, people): self.labels, self.people = labels, people
    def name(self, var): return self.labels[var.name]
    def render(self, f):
        if isinstance(f, Eq): return f"{self.name(f.x)} belongs to {self.people[f.value]}."
        if isinstance(f, Ne): return f"{self.name(f.x)} does not belong to {self.people[f.value]}."
        if isinstance(f, EqVar): return f"{self.name(f.x)} and {self.name(f.y)} belong to the same person."
        if isinstance(f, NeVar): return f"{self.name(f.x)} and {self.name(f.y)} belong to different people."
        return super().render(f)
