"""Query-aware multi-order clue selection."""

from __future__ import annotations

from dataclasses import dataclass

from .ir import Eq, canonical_unique, operator_name
from .metrics import analyze
from .solver import CSPSolver


@dataclass(frozen=True)
class Query:
    kind: str
    var: object
    answer: object
    text: str


@dataclass
class SelectedInstance:
    query: Query
    clues: list
    metrics: dict


def _direct_answer(clue, query):
    if not isinstance(clue, Eq): return False
    if clue.x == query.var and clue.value == query.answer: return True
    # In Latin grids, givens in the queried row/column turn the task into a
    # shallow completion shortcut. Relations and cross-grid interactions remain.
    qname, cname = query.var.name, clue.x.name
    if qname.startswith("r") and "c" in qname and cname.startswith("r") and "c" in cname:
        qr, qc = qname[1:].split("c"); cr, cc = cname[1:].split("c")
        return qr == cr or qc == cc
    return False


def _sufficient(solver, clues, query):
    if query.kind in {"scalar", "entity"}: return solver.unique_value(query.var, clues) == query.answer
    if query.kind == "count": return len(solver.possible_values(query.var, clues)) == query.answer
    if query.kind == "possibility":
        possible = query.answer[0]
        return (query.answer[1] in solver.possible_values(query.var, clues)) == possible
    return False


def minimize(solver, pool, query, rng, n_orders=6):
    """Find several path-dependent greedy minima and keep the strongest one."""
    candidates = []
    usable = [c for c in canonical_unique(pool) if not _direct_answer(c, query)]
    # Compositional pools can be large. Retain every query-local clue and sample
    # a bounded, structurally varied context; this keeps multi-order minimization
    # cheap enough for dataset generation without planting a proof.
    local = [c for c in usable if query.var in c.variables()]
    remote = [c for c in usable if query.var not in c.variables()]
    local.sort(key=lambda c: (c.complexity(), repr(c.canonical())))
    if len(local) > 24:
        atoms, compounds = local[:16], local[16:]; rng.shuffle(compounds); local = atoms + compounds[:8]
    rng.shuffle(remote)
    usable = canonical_unique(local + remote[:max(0, 32-len(local))])
    for _ in range(min(n_orders, 2)):
        order = usable.copy(); rng.shuffle(order)
        selected = []
        for clue in order:
            selected.append(clue)
            if _sufficient(solver, selected, query): break
        if not _sufficient(solver, selected, query): continue
        deletion = selected.copy(); rng.shuffle(deletion)
        for clue in deletion:
            trial = selected.copy(); trial.remove(clue)
            if _sufficient(solver, trial, query): selected = trial
        candidates.append(selected)
    if not candidates: return None
    clues = max(candidates, key=lambda x: (len({operator_name(c) for c in x}), -len(x)))
    return SelectedInstance(query, clues, analyze(solver, clues, query))


def select_instance(variables, base, pool, queries, rng, n_orders=6):
    """Analyze shuffled queries after the system exists; never plant a query proof."""
    solver = CSPSolver(variables, base)
    choices = []
    query_order = list(queries); rng.shuffle(query_order)
    for query in query_order[:min(2, len(query_order))]:
        chosen = minimize(solver, pool, query, rng, n_orders)
        if chosen and len(chosen.clues) >= 2:
            choices.append(chosen)
    if not choices: return None
    # Prefer interaction and operator diversity, but do not make one rigid subcase universal.
    return max(choices, key=lambda x: (
        min(x.metrics["minimum_wrong_answer_core_size"], 4),
        min(len(x.metrics["operator_histogram"]), 3),
        x.metrics["query_forced_round"] or 0,
        -len(x.clues),
    ))
