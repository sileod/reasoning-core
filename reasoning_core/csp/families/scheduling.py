from ..ir import AllDifferent, Distance, Eq, Lt, Ne
from ..render import SymbolicRenderer
from ..selection import Query
from .base import World, true_composites


class SchedulingFamily:
    name = "scheduling"
    def sample_world(self, rng, size):
        from ..ir import Var
        n = max(4, min(7, size + 1)); variables = tuple(Var(chr(65+i), range(1, n+1)) for i in range(n))
        slots = rng.sample(range(1, n+1), n)
        return World(variables, dict(zip(variables, slots)), {"n": n})
    def variables(self, w): return w.variables
    def base_constraints(self, w): return [AllDifferent(w.variables)]
    def candidate_formulas(self, w, rng):
        true, false = [], []
        for v in w.variables:
            true.append(Eq(v, w.witness[v])); false.append(Ne(v, w.witness[v]))
            true.extend(Ne(v, x) for x in v.domain if x != w.witness[v])
        for i, a in enumerate(w.variables):
            for b in w.variables[i+1:]:
                earlier, later = (a,b) if w.witness[a] < w.witness[b] else (b,a)
                true.append(Lt(earlier, later)); false.append(Lt(later, earlier))
                if abs(w.witness[a]-w.witness[b]) <= 2: true.append(Distance(a,b,abs(w.witness[a]-w.witness[b])))
        return true + true_composites(rng, true, false, 12), false
    def queries(self, w): return [Query("scalar", v, w.witness[v], f"What slot contains task {v.name}?") for v in w.variables]
    def renderer(self, w): return SymbolicRenderer()
    def answer(self, w, q): return str(q.answer)
    def invariant(self, w): return f"Tasks A-{w.variables[-1].name} occupy slots 1-{w.data['n']}, one task per slot."
    def domains_text(self, w): return ""

