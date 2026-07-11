"""Query-aware finite-domain CSPs over a shared semantic representation."""

from __future__ import annotations

import ast
import json
import random
from dataclasses import dataclass, replace
from typing import Optional

from reasoning_core.csp.families import ALIASES, FAMILIES
from reasoning_core.csp.generator import generate_instance, render_instance
from reasoning_core.csp.ir import Eq, Ne, operator_name
from reasoning_core.csp.metrics import analyze, split_key
from reasoning_core.csp.solver import CSPSolver
from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround


@dataclass
class ConstraintSatisfactionConfig(Config):
    n_vars: int = 2
    max_domain: int = 2
    n_constraints: int = 3
    coef_bound: int = 3
    unsat_prob: float = 0.15
    max_tries: int = 64

    # Compatibility aliases: attribute -> assignment, linear -> numeric.
    model_mode: str = "any"
    solve_mode: str = "query"  # query | all | min; lex_all aliases all
    max_solutions: Optional[int] = 256

    # Semantic selection controls.
    minimization_orders: int = 6
    counterfactual_prob: float = 0.15

    # Retained compatibility knobs. Numeric structure is now expressed by the IR.
    structure_mode: str = "any"
    max_arity: int = 3
    edge_prob: float = 0.25
    n_clusters: int = 3
    p_in: float = 0.6
    p_out: float = 0.1
    grid_width: Optional[int] = None

    def apply_difficulty(self, level):
        self.n_vars = sround(self.n_vars + 0.6 * level)
        self.max_domain = sround(self.max_domain + 0.4 * level)
        self.n_constraints = sround(self.n_constraints + 1.1 * level)
        self.coef_bound = sround(self.coef_bound + 0.3 * level)
        self.minimization_orders = sround(self.minimization_orders + 0.5 * level)


CSPConfig = ConstraintSatisfactionConfig


class ConstraintSatisfaction(Task):
    summary = "Solve query-aware assignment, graph, scheduling, grid, set, and numeric CSPs."
    config_cls = ConstraintSatisfactionConfig

    def __init__(self, config=None):
        super().__init__(config=config or self.config_cls())
        c = self.config
        if c.solve_mode.lower() == "lex_all": c.solve_mode = "all"
        modes = set(FAMILIES) | set(ALIASES) | {"any"}
        if c.model_mode.lower() not in modes: raise ValueError(f"Unknown model_mode: {c.model_mode!r}")
        if c.solve_mode.lower() not in {"query", "all", "min"}: raise ValueError(f"Unknown solve_mode: {c.solve_mode!r}")
        if c.structure_mode.lower() not in {"complete", "random", "graph", "grid", "clustered", "any"}:
            raise ValueError(f"Unknown structure_mode: {c.structure_mode!r}")
        if min(c.coef_bound, c.max_tries, c.max_arity, c.minimization_orders) <= 0:
            raise ValueError("coef_bound, max_tries, max_arity, and minimization_orders must be positive")
        if c.max_solutions is not None and c.max_solutions <= 0: raise ValueError("max_solutions must be positive or None")
        if c.grid_width is not None and c.grid_width <= 0: raise ValueError("grid_width must be positive or None")
        for field in ("unsat_prob", "counterfactual_prob", "edge_prob", "p_in", "p_out"):
            if not 0 <= getattr(c, field) <= 1: raise ValueError(f"{field} must be between 0 and 1")

    def generate_entry(self):
        c, rng = self.config, random
        requested = c.model_mode.lower()
        family = rng.choices(list(FAMILIES), weights=[3, 2, 3, 2, 2, 3])[0] if requested == "any" else ALIASES.get(requested, requested)
        instance = generate_instance(
            family, rng, max(3, int(c.n_vars) + (2 if family != "numeric" else 0)),
            max_tries=int(c.max_tries), n_orders=int(c.minimization_orders),
            max_domain=max(2, int(c.max_domain)), coef_bound=int(c.coef_bound),
        )
        clues, answer, solve_mode = list(instance.clues), instance.answer, c.solve_mode.lower()
        query, query_type = instance.query, instance.query.kind

        if instance.counterfactual_pair and rng.random() < c.counterfactual_prob:
            index, mutation, changed_value, changed_answer = instance.counterfactual_pair
            clues[index], answer, query_type = mutation, changed_answer, "counterfactual"
            query = replace(query, answer=changed_value)

        if family == "numeric" and rng.random() < c.unsat_prob:
            q, value = instance.query.var, instance.query.answer
            base_solver = CSPSolver(instance.world.variables, instance.base)
            target = max(2, int(c.n_constraints)); contradiction = None
            mutations = list(instance.counterfactuals); rng.shuffle(mutations)
            for mutation in mutations:
                trial = clues + [mutation]
                if len(trial) <= target and not base_solver.is_sat(trial):
                    contradiction = trial; break
            if contradiction is None: contradiction = [Eq(q, value), Ne(q, value)]
            fillers = [c for c in clues if c not in contradiction]
            fillers += [Ne(v, x) for v in instance.world.variables for x in v.domain
                        if x != instance.world.witness[v]]
            clues = (contradiction + fillers)[:target]
            answer, query_type = "UNSAT", "consistency"

        # Full-assignment modes remain available for backwards compatibility, but
        # query mode is the SFT-oriented default.
        if family == "numeric" and solve_mode in {"all", "min"}:
            active_solver = CSPSolver(instance.world.variables, instance.base, clues)
            solutions, overflow = active_solver.solutions(limit=c.max_solutions) if solve_mode == "all" else (None, False)
            if overflow:
                clues += [Eq(v, instance.world.witness[v]) for v in instance.world.variables]
                solutions, overflow = CSPSolver(instance.world.variables, instance.base, clues).solutions(limit=c.max_solutions)
            if overflow: raise RuntimeError("Numeric CSP exceeded max_solutions after bounded completion")
            if solve_mode == "min":
                solution = active_solver.lex_solution()
                answer = "UNSAT" if solution is None else json.dumps(list(solution))
            elif not solutions: answer = "UNSAT"
            else: answer = json.dumps([list(x) for x in solutions])
            query_type = "all_solutions" if solve_mode == "all" else "lexicographic_solution"

        rendered = [formula.render(instance.renderer) for formula in clues]
        prompt = render_instance(instance)
        if clues != instance.clues:
            family_adapter = FAMILIES[family]
            preamble = "\n".join(x for x in (family_adapter.domains_text(instance.world), family_adapter.invariant(instance.world)) if x)
            prompt = f"{preamble}\n\nConstraints:\n" + "\n".join(f"{i}. {x}" for i,x in enumerate(rendered,1))
        if query_type == "all_solutions":
            prompt += "\n\nQuestion: Enumerate all satisfying assignments in variable order [" + ", ".join(v.name for v in instance.world.variables) + "]?\nThe answer is a lexicographically sorted JSON list of lists, or UNSAT."
        elif query_type == "lexicographic_solution":
            prompt += "\n\nQuestion: What is the lexicographically smallest satisfying assignment in variable order [" + ", ".join(v.name for v in instance.world.variables) + "]?\nThe answer is a JSON list of integers, or UNSAT."
        elif query_type == "consistency":
            prompt += "\n\nQuestion: Are these constraints consistent?\nAnswer with SAT or UNSAT."
        elif query_type == "counterfactual":
            prompt += f"\n\nQuestion: {instance.query.text}\nAnswer with one name or integer."

        metrics = (analyze(CSPSolver(instance.world.variables, instance.base), clues, query)
                   if query_type == "counterfactual" else dict(instance.metrics))
        if answer == "UNSAT":
            active = list(clues); consistency_solver = CSPSolver(instance.world.variables, instance.base)
            for clue in list(active):
                trial = active.copy(); trial.remove(clue)
                if not consistency_solver.is_sat(trial): active = trial
            metrics.update({
                "consistency_core_size": len(active),
                "displayed_clue_essentiality": round(len(active) / len(clues), 4),
                "operator_histogram": {name: sum(operator_name(c) == name for c in clues)
                                       for name in sorted({operator_name(c) for c in clues})},
            })
        metadata = edict({
            "model_mode": requested if requested != "any" else family,
            "family": family, "solve_mode": solve_mode, "query_type": query_type,
            "query": ((int(instance.query.var.name.split('c')[0][1:]), int(instance.query.var.name.split('c')[1]))
                      if family == "grid" else instance.query.var.name),
            "query_var": instance.query.var.name, "clues": rendered, "constraints": rendered,
            "canonical_clues": [repr(x.canonical()) for x in clues],
            "base_constraints": [repr(x.canonical()) for x in instance.base],
            "counterfactual_candidates": [repr(x.canonical()) for x in instance.counterfactuals],
            "counterfactual_applied": query_type == "counterfactual",
            "metrics": metrics, "split_key": split_key(family, instance.base, clues, query_type),
            "solution": None if answer == "UNSAT" else answer,
            "prompt": prompt, "payload": {"instance": prompt.rsplit("\n\nQuestion:", 1)[0]},
            "render_seed": 0,
        })
        if family == "grid":
            metadata.relational_clues_required = any(" < " in x or " > " in x for x in rendered)
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        return metadata.prompt

    def score_answer(self, answer, entry):
        expected = entry.answer if hasattr(entry, "answer") else entry["answer"]
        mode = (entry.metadata if hasattr(entry, "metadata") else entry["metadata"]).get("query_type")
        if mode not in {"all_solutions", "lexicographic_solution"}:
            return float(str(answer).strip().casefold() == str(expected).strip().casefold())
        def parse(value):
            if not isinstance(value, str): return None
            if value.strip().upper() == "UNSAT": return "UNSAT"
            try:
                result = ast.literal_eval(value.strip())
                if isinstance(result, list) and all(type(x) is int for x in result): return result
                if isinstance(result, list) and all(isinstance(row,list) and all(type(x) is int for x in row) for row in result): return result
            except (ValueError, SyntaxError): pass
            return None
        return float(parse(answer) == parse(expected))


if __name__ == "__main__":
    task = ConstraintSatisfaction()
    problem = task.generate_entry()
    print(task.render_prompt(problem.metadata)); print(problem.answer)
