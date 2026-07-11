from ..ir import AllDifferent, Eq, Lt, Ne
from ..render import SymbolicRenderer
from ..selection import Query
from .base import World, true_composites


class GridFamily:
    name = "grid"
    def sample_world(self, rng, size):
        from ..ir import Var
        n = max(3, min(5, size)); symbols = rng.sample(range(1, n + 1), n)
        rows = [[symbols[(r + c) % n] for c in range(n)] for r in range(n)]; rng.shuffle(rows)
        variables = tuple(Var(f"r{r+1}c{c+1}", range(1, n + 1)) for r in range(n) for c in range(n))
        return World(variables, {v: rows[i // n][i % n] for i, v in enumerate(variables)}, {"n": n})
    def variables(self, w): return w.variables
    def base_constraints(self, w):
        n = w.data["n"]
        return [AllDifferent(w.variables[r*n:(r+1)*n]) for r in range(n)] + [AllDifferent(w.variables[c::n]) for c in range(n)]
    def candidate_formulas(self, w, rng):
        n, true, false = w.data["n"], [], []
        for v in w.variables:
            true.append(Eq(v, w.witness[v])); false.append(Ne(v, w.witness[v]))
            true.extend(Ne(v, x) for x in v.domain if x != w.witness[v])
        for r in range(n):
            for c in range(n):
                a = w.variables[r*n+c]
                for dr, dc in ((1, 0), (0, 1)):
                    if r+dr < n and c+dc < n:
                        b = w.variables[(r+dr)*n+c+dc]
                        (true if w.witness[a] < w.witness[b] else false).append(Lt(a, b))
                        (true if w.witness[b] < w.witness[a] else false).append(Lt(b, a))
        return true + true_composites(rng, true, false, 12), false
    def queries(self, w): return [Query("scalar", v, w.witness[v], f"What is {v.name}?") for v in w.variables]
    def renderer(self, w): return SymbolicRenderer()
    def answer(self, w, q): return str(q.answer)
    def invariant(self, w): return f"In this {w.data['n']}x{w.data['n']} grid, each row and column contains 1..{w.data['n']} once."
    def domains_text(self, w): return ""

