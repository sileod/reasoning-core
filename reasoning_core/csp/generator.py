"""Shared family-independent instance generation pipeline."""

from dataclasses import dataclass, replace

from .families import get_family
from .metrics import split_key
from .selection import select_instance


@dataclass
class GeneratedInstance:
    family: str
    world: object
    base: list
    clues: list
    counterfactuals: list
    counterfactual_pair: object
    query: object
    answer: str
    metrics: dict
    split_key: dict
    renderer: object


def generate_instance(family_name, rng, size, max_tries=64, n_orders=6, max_domain=4, coef_bound=3):
    family = get_family(family_name)
    if family.name == "numeric": family.coef_bound = coef_bound
    for _ in range(max_tries):
        world = family.sample_world(rng,size,max_domain) if family.name == "numeric" else family.sample_world(rng,size)
        base = family.base_constraints(world)
        pool, false_pool = family.candidate_formulas(world,rng)
        selected = select_instance(family.variables(world),base,pool,family.queries(world),rng,n_orders)
        if selected is None: continue
        # Matched counterfactual candidates are semantic mutations, independently false in the witness.
        counterfactuals = false_pool[:min(8,len(false_pool))]
        counterfactual_pair = None
        from .solver import CSPSolver
        solver = CSPSolver(family.variables(world), base)
        mutations = [(i, f) for i, clue in enumerate(selected.clues) for f in counterfactuals
                     if f.canonical()[0] == clue.canonical()[0]]
        rng.shuffle(mutations)
        for index, mutation in mutations[:16]:
            changed = selected.clues[:index] + [mutation] + selected.clues[index+1:]
            values = solver.possible_values(selected.query.var, changed)
            if len(values) == 1 and values[0] != selected.query.answer:
                new_query = replace(selected.query, answer=values[0])
                counterfactual_pair = (index, mutation, values[0], family.answer(world, new_query))
                break
        return GeneratedInstance(
            family.name,world,base,selected.clues,counterfactuals,counterfactual_pair,selected.query,
            family.answer(world,selected.query),selected.metrics,
            split_key(family.name,base,selected.clues,selected.query.kind),family.renderer(world),
        )
    raise RuntimeError(f"Failed to generate a quality {family.name} CSP after {max_tries} attempts")


def render_instance(instance):
    family = get_family(instance.family); world = instance.world
    preamble = "\n".join(x for x in (family.domains_text(world),family.invariant(world)) if x)
    clues = "\n".join(f"{i}. {c.render(instance.renderer)}" for i,c in enumerate(instance.clues,1))
    return f"{preamble}\n\nConstraints:\n{clues}\n\nQuestion: {instance.query.text}\nAnswer with one name or integer."
