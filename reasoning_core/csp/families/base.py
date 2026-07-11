from dataclasses import dataclass, field

import z3

from ..ir import Implies, Or, Xor


@dataclass
class World:
    variables: tuple
    witness: dict
    data: dict = field(default_factory=dict)


def holds(formula, witness):
    ctx = {v.name: z3.Int(v.name) for v in formula.variables()}
    expression = formula.to_z3(ctx)
    pairs = [(ctx[v.name], z3.IntVal(witness[v])) for v in formula.variables()]
    return z3.is_true(z3.simplify(z3.substitute(expression, *pairs)))


def true_composites(rng, true_atoms, false_atoms, limit=16):
    """Build shallow true formulas; false atoms are retained for counterfactual metadata."""
    out = []
    if not true_atoms or not false_atoms: return out
    for _ in range(limit):
        truth = rng.choice(true_atoms); miss = rng.choice(false_atoms)
        out.extend((Or((truth, miss)), Xor((truth, miss)), Implies(miss, rng.choice(true_atoms))))
    rng.shuffle(out)
    return out[:limit]

