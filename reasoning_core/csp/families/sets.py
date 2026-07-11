from ..ir import AtMost, Eq, Exactly, Implies, Ne
from ..render import SymbolicRenderer
from ..selection import Query
from .base import World, true_composites


class SetFamily:
    name = "sets"
    def sample_world(self, rng, size):
        from ..ir import Var
        n = max(4, min(8, size + 2)); variables = tuple(Var(f"m{i}", (0,1), "bool") for i in range(n))
        witness = {v: rng.randrange(2) for v in variables}
        if not any(witness.values()): witness[rng.choice(variables)] = 1
        return World(variables, witness, {"n": n})
    def variables(self, w): return w.variables
    def base_constraints(self, w): return []
    def candidate_formulas(self, w, rng):
        true, false = [], []
        for v in w.variables:
            true.append(Eq(v, w.witness[v])); false.append(Eq(v, 1-w.witness[v]))
        for _ in range(2*w.data["n"]):
            subset = tuple(rng.sample(w.variables, rng.randint(2, min(4, len(w.variables)))))
            atoms = tuple(Eq(v, 1) for v in subset); count = sum(w.witness[v] for v in subset)
            true.extend((Exactly(count, atoms), AtMost(count, atoms)))
            if count < len(subset): false.append(Exactly(count+1, atoms))
        return true + true_composites(rng, true, false, 10), false
    def queries(self, w): return [Query("scalar", v, w.witness[v], f"Is {v.name} selected (1 or 0)?") for v in w.variables]
    def renderer(self, w): return SymbolicRenderer()
    def answer(self, w, q): return str(q.answer)
    def invariant(self, w): return "Each membership variable is 0 (not selected) or 1 (selected)."
    def domains_text(self, w): return ""

