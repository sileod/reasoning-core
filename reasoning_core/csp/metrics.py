"""Solver-independent, interpretable finite-domain difficulty measurements."""

from __future__ import annotations

from collections import Counter
from itertools import product
from statistics import median

import z3

from .ir import AllDifferent, Eq, Formula, operator_name
from .solver import CSPSolver


def _supported(formula, target, value, domains):
    """Whether a value has local support in one constraint (generalized arc consistency)."""
    variables = sorted(formula.variables(), key=lambda v: v.name)
    ctx = {v.name: z3.Int(v.name) for v in variables}
    expression = formula.to_z3(ctx)
    for values in product(*(domains[v] if v != target else (value,) for v in variables)):
        substituted = z3.substitute(expression, *[(ctx[v.name], z3.IntVal(x)) for v, x in zip(variables, values)])
        if z3.is_true(z3.simplify(substituted)):
            return True
    return False


def propagate(variables, formulas, max_rounds=32):
    """Apply local support and singleton propagation until a fixed point."""
    domains = {v: list(v.domain) for v in variables}
    rounds, forced_at = 0, {}
    for round_no in range(1, max_rounds + 1):
        changed = False
        for formula in formulas:
            if any(not domains[v] for v in formula.variables()): continue
            if isinstance(formula, AllDifferent):
                singletons = {domains[v][0] for v in formula.vars if len(domains[v]) == 1}
                for var in formula.vars:
                    if len(domains[var]) > 1:
                        kept = [x for x in domains[var] if x not in singletons]
                        if kept != domains[var]:
                            domains[var], changed = kept, True
                            if len(kept) == 1: forced_at.setdefault(var.name, round_no)
                continue
            # Large global constraints have specialized propagation above; avoid
            # exponential tuple enumeration for arbitrary formulas.
            if len(formula.variables()) > 5: continue
            for var in formula.variables():
                kept = [x for x in domains[var] if _supported(formula, var, x, domains)]
                if len(kept) < len(domains[var]):
                    domains[var], changed = kept, True
                    if len(kept) == 1: forced_at.setdefault(var.name, round_no)
        if not changed: break
        rounds = round_no
    return domains, rounds, forced_at


def backbone_saturation(solver, clues):
    zsolver = solver.solver(clues)
    if zsolver.check() != z3.sat: return 0.0
    model, forced = zsolver.model(), 0
    for var in solver.variables:
        value = model.eval(solver.ctx[var.name], model_completion=True)
        zsolver.push(); zsolver.add(solver.ctx[var.name] != value)
        forced += zsolver.check() == z3.unsat
        zsolver.pop()
    return forced / len(solver.variables)


def branching_metrics(solver, clues, domains):
    """Deterministic fail-first search after propagation; secondary difficulty only."""
    guesses = failed = max_depth = 0

    def visit(current, depth):
        nonlocal guesses, failed, max_depth
        max_depth = max(max_depth, depth)
        if not solver.solver(clues, domains=current).check() == z3.sat:
            failed += 1; return False
        open_vars = [v for v in solver.variables if len(current[v]) > 1]
        if not open_vars: return True
        var = min(open_vars, key=lambda v: (len(current[v]), v.name)); guesses += 1
        for value in current[var]:
            child = {v: list(xs) for v, xs in current.items()}; child[var] = [value]
            if visit(child, depth + 1): return True
        return False

    visit(domains, 0)
    return {"guesses": guesses, "failed_branches": failed, "max_depth": max_depth}


def analyze(solver: CSPSolver, clues, query):
    base_values = solver.possible_values(query.var, ())
    values = solver.possible_values(query.var, clues)
    saturation = backbone_saturation(solver, clues)
    leave_one_out = []
    for i in range(len(clues)):
        reduced = clues[:i] + clues[i + 1:]
        leave_one_out.append(round(saturation - backbone_saturation(solver, reduced), 4))
    cores = [solver.refutation_core(query.var, v, clues) for v in query.var.domain if v not in values]
    domains, rounds, forced_at = propagate(solver.variables, (*solver.base, *clues))
    kinds = Counter(operator_name(c) for c in clues)
    essential_query = [solver.possible_values(query.var, clues[:i] + clues[i + 1:]) != values for i in range(len(clues))]
    full_unique = solver.full_unique(clues)
    essential_full = [full_unique and not solver.full_unique(clues[:i] + clues[i + 1:]) for i in range(len(clues))]
    essential_wrong = [any(clue in core for core in cores) for clue in clues]
    accepted = [a or b or c for a,b,c in zip(essential_query,essential_full,essential_wrong)]
    base_essential = []
    for i, invariant in enumerate(solver.base):
        reduced = CSPSolver(solver.variables, solver.base[:i] + solver.base[i+1:])
        base_essential.append(reduced.possible_values(query.var, clues) != values)
    groups = sorted({v.name.split("_",1)[0] for c in clues for v in c.variables()})
    core_details = [{
        "size": len(core),
        "variables_touched": len(set().union(*(c.variables() for c in core))) if core else 0,
        "operator_types": sorted({operator_name(c) for c in core}),
        "semantic_groups": sorted({v.name.split("_",1)[0] for c in core for v in c.variables()}),
    } for core in cores]
    return {
        "backbone_saturation": round(saturation, 4),
        "leave_one_out_effect": leave_one_out,
        "query_domain_before": base_values,
        "query_domain_after": values,
        "wrong_answer_core_sizes": [len(c) for c in cores],
        "wrong_answer_cores": core_details,
        "minimum_wrong_answer_core_size": min(map(len, cores), default=0),
        "median_wrong_answer_core_size": median(map(len, cores)) if cores else 0,
        "operator_histogram": dict(sorted(kinds.items())),
        "variables_touched": len(set().union(*(c.variables() for c in clues))),
        "semantic_groups_touched": groups,
        "propagation_rounds": rounds,
        "query_forced_round": forced_at.get(query.var.name),
        "essential_for_query": essential_query,
        "essential_for_full_solution": essential_full,
        "essential_for_some_wrong_answer": essential_wrong,
        "displayed_clue_essentiality": round(sum(accepted) / len(clues), 4) if clues else 0,
        "query_essentiality": round(sum(essential_query) / len(clues), 4) if clues else 0,
        "base_invariant_essential": base_essential,
        "global_invariant_essential": any(
            flag and isinstance(formula, AllDifferent)
            for flag, formula in zip(base_essential, solver.base)
        ),
        "branching": branching_metrics(solver, clues, domains),
    }


def split_key(family, base, clues, query_type):
    """A name-invariant structural key suitable for leakage-resistant splits."""
    def skeleton(formula):
        canonical = formula.canonical()
        names = {v.name: f"v{i}" for i, v in enumerate(sorted(formula.variables(), key=lambda x: x.name))}
        text = repr(canonical)
        for old, new in sorted(names.items(), key=lambda p: -len(p[0])): text = text.replace(old, new)
        return text
    import networkx as nx
    graph = nx.Graph()
    formulas = list(base) + list(clues)
    variables = sorted(set().union(*(f.variables() for f in formulas)), key=lambda v: v.name)
    for i, var in enumerate(variables): graph.add_node(f"v{i}", label=f"var:{var.sort}:{len(var.domain)}")
    indices = {v: i for i,v in enumerate(variables)}
    for i, formula in enumerate(formulas):
        node = f"c{i}"; graph.add_node(node, label=f"constraint:{operator_name(formula)}")
        for var in formula.variables(): graph.add_edge(node, f"v{indices[var]}")
    incidence_hash = nx.weisfeiler_lehman_graph_hash(graph, node_attr="label")
    return {
        "family": family,
        "base_constraint_skeleton": sorted(skeleton(x) for x in base),
        "clue_formula_skeletons": sorted(skeleton(x) for x in clues),
        "query_type": query_type,
        "incidence_graph": incidence_hash,
        "operator_histogram": dict(Counter(operator_name(x) for x in clues)),
    }
