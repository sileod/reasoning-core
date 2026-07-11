from ..ir import Eq, Ne, NeVar
from ..render import SymbolicRenderer
from ..selection import Query
from .base import World, true_composites


class GraphFamily:
    name = "graph"
    def sample_world(self, rng, size):
        from ..ir import Var
        n, colors = max(4, min(8, size + 1)), 3
        variables = tuple(Var(f"v{i}", range(colors)) for i in range(n))
        witness = {v: rng.randrange(colors) for v in variables}
        edges = [(variables[i], variables[j]) for i in range(n) for j in range(i+1, n)
                 if witness[variables[i]] != witness[variables[j]] and rng.random() < .45]
        return World(variables, witness, {"edges": edges, "colors": colors})
    def variables(self, w): return w.variables
    def base_constraints(self, w): return [NeVar(a, b) for a, b in w.data["edges"]]
    def candidate_formulas(self, w, rng):
        true, false = [], []
        for v in w.variables:
            true += [Eq(v, w.witness[v]), *[Ne(v, x) for x in v.domain if x != w.witness[v]]]
            false.append(Ne(v, w.witness[v]))
        return true + true_composites(rng, true, false, 10), false
    def queries(self, w): return [Query("scalar", v, w.witness[v], f"What color number is {v.name}?") for v in w.variables]
    def renderer(self, w): return SymbolicRenderer()
    def answer(self, w, q): return str(q.answer)
    def invariant(self, w): return "Adjacent vertices have different colors numbered 0..2."
    def domains_text(self, w): return "Edges: " + ", ".join(f"{a.name}-{b.name}" for a,b in w.data["edges"]) + "."

