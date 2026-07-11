from ..ir import AllDifferent, Eq, Linear, Mod, Ne
from ..render import SymbolicRenderer
from ..selection import Query
from .base import World, true_composites


class NumericFamily:
    name = "numeric"
    def __init__(self, coef_bound=3): self.coef_bound = coef_bound
    def sample_world(self, rng, size, max_domain=4):
        from ..ir import Var
        n = max(2, min(7, size)); variables = tuple(Var(f"x{i}", range(rng.randint(2,max_domain)+1)) for i in range(n))
        return World(variables, {v: rng.choice(v.domain) for v in variables}, {})
    def variables(self, w): return w.variables
    def base_constraints(self, w): return []
    def candidate_formulas(self, w, rng):
        true, false = [], []
        for v in w.variables:
            true += [Eq(v,w.witness[v]), *[Ne(v,x) for x in v.domain if x != w.witness[v]]]
            false.append(Ne(v,w.witness[v]))
        for _ in range(5*len(w.variables)):
            scope = rng.sample(w.variables, rng.randint(1,min(3,len(w.variables))))
            coeffs = [rng.choice([x for x in range(-self.coef_bound,self.coef_bound+1) if x]) for _ in scope]
            value = sum(a*w.witness[v] for a,v in zip(coeffs,scope)); op = rng.choice(("==","<=",">=","!="))
            rhs = value if op == "==" else value+rng.randint(0,2) if op == "<=" else value-rng.randint(0,2) if op == ">=" else value+rng.choice((-2,-1,1,2))
            true.append(Linear(coeffs,scope,op,rhs))
            modulus = rng.randint(2,5); expr = Linear(coeffs,scope,"==",value)
            true.append(Mod(expr,modulus,value%modulus)); false.append(Mod(expr,modulus,(value+1)%modulus))
        distinct = [v for v in w.variables if list(w.witness.values()).count(w.witness[v]) == 1]
        if len(distinct)>1: true.append(AllDifferent(distinct))
        return true + true_composites(rng, true, false, 12), false
    def queries(self, w): return [Query("scalar", v, w.witness[v], f"What is {v.name}?") for v in w.variables]
    def renderer(self, w): return SymbolicRenderer()
    def answer(self, w, q): return str(q.answer)
    def invariant(self, w): return "All variables are integers in their listed finite domains."
    def domains_text(self, w): return "Domains: " + ", ".join(f"{v.name} in {{{', '.join(map(str,v.domain))}}}" for v in w.variables) + "."

