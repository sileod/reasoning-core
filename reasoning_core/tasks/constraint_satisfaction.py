from dataclasses import dataclass
import ast
import json
import math
import random
from typing import Optional

from reasoning_core.template import Task, Problem, Config, edict
from z3 import Distinct, Int, Optimize, Or, Solver, Sum, sat


@dataclass
class ConstraintSatisfactionConfig(Config):
    n_vars: int = 2
    max_domain: int = 2
    n_constraints: int = 3
    coef_bound: int = 3
    unsat_prob: float = 0.15
    max_tries: int = 64

    # Structure: "random" | "graph" | "grid" | "clustered" | "any"
    structure_mode: str = "any"
    max_arity: int = 3

    # Solve mode: "all" (enumerate all) or "min" (lex-smallest). 
    # If "all" overflows `max_solutions`, it automatically falls back to "min".
    solve_mode: str = "all"
    max_solutions: Optional[int] = 256

    edge_prob: float = 0.25
    n_clusters: int = 3
    p_in: float = 0.6
    p_out: float = 0.1
    grid_width: Optional[int] = None
    model_mode: str = "any"  # "linear" | "attribute" | "grid" | "any"

    def update(self, c=1):
        self.n_vars += 0.6 * c
        self.max_domain += 0.4 * c
        self.n_constraints += 1.1 * c
        self.coef_bound += 0.3 * c
        self.max_arity = min(4, self.max_arity + int(c >= 3))


CSPConfig = ConstraintSatisfactionConfig


class ConstraintSatisfaction(Task):

    def __init__(self, config=None):
        super().__init__(config=config or CSPConfig())

    def _rng(self):
        return random.Random(self.config.seed)

    def _possible_values(self, solver, var, values):
        out = []
        for v in values:
            solver.push()
            solver.add(var == v)
            if solver.check() == sat:
                out.append(v)
            solver.pop()
        return out

    def _unique_value(self, solver, var, values):
        vals = self._possible_values(solver, var, values)
        return vals[0] if len(vals) == 1 else None

    def _build_neighbors(self, rng, n, mode):
        nbrs = [set() for _ in range(n)]

        def link(i, j):
            if i != j:
                nbrs[i].add(j); nbrs[j].add(i)

        if mode == "random":
            for i in range(n): nbrs[i] = set(range(n)) - {i}
        elif mode == "graph":
            for i in range(n):
                for j in range(i + 1, n):
                    if rng.random() < self.config.edge_prob: link(i, j)
        elif mode == "grid":
            w = self.config.grid_width or max(1, round(math.sqrt(n)))
            h = (n + w - 1) // w
            for r in range(h):
                for c in range(w):
                    i = r * w + c
                    if i < n:
                        for dr, dc in ((1, 0), (0, 1)):
                            j = (r + dr) * w + (c + dc)
                            if r + dr < h and c + dc < w and j < n: link(i, j)
        elif mode == "clustered":
            g = max(1, min(self.config.n_clusters, n))
            cluster_of = [rng.randrange(g) for _ in range(n)]
            for i in range(n):
                for j in range(i + 1, n):
                    p = self.config.p_in if cluster_of[i] == cluster_of[j] else self.config.p_out
                    if rng.random() < p: link(i, j)

        for i in range(n):
            if not nbrs[i]: link(i, rng.choice([x for x in range(n) if x != i]))
        return nbrs

    def _sample_scope(self, rng, neighbors, n, mode):
        k = rng.randint(1, max(1, min(self.config.max_arity, n)))
        if mode == "random" or k == 1:
            return sorted(rng.sample(range(n), k))

        seed = rng.randrange(n)
        scope, frontier = {seed}, set(neighbors[seed])
        while len(scope) < k and frontier:
            j = rng.choice(tuple(frontier))
            scope.add(j)
            frontier.update(neighbors[j])
            frontier.difference_update(scope)

        if len(scope) < k:
            rest = [j for j in range(n) if j not in scope]
            if rest: scope.update(rng.sample(rest, min(k - len(scope), len(rest))))
        return sorted(scope)

    def _sample_constraint(self, rng, idx, witness, coef_bound):
        kind = rng.choices(["lin", "mod", "alldiff"], weights=[6, 2, 2] if len(idx) >= 2 else [7, 3, 0])[0]

        if kind == "lin":
            coeffs = [rng.choice([x for x in range(-coef_bound, coef_bound + 1) if x != 0]) for _ in idx]
            val = sum(a * witness[i] for a, i in zip(coeffs, idx))
            op = rng.choices(["==", "!=", "<=", ">="], weights=[3, 2, 3, 3])[0]
            if op == "==": rhs = val
            elif op == "!=": rhs = val + rng.choice([x for x in range(-(coef_bound + 2), coef_bound + 3) if x != 0])
            elif op == "<=": rhs = val + rng.randint(0, coef_bound + 1)
            else: rhs = val - rng.randint(0, coef_bound + 1)
            return {"type": "lin", "idx": idx, "coeffs": coeffs, "op": op, "rhs": rhs}

        if kind == "mod":
            coeffs = [rng.randint(1, coef_bound) for _ in idx]
            mod = rng.randint(2, max(2, coef_bound + 2))
            rem = sum(a * witness[i] for a, i in zip(coeffs, idx)) % mod
            return {"type": "mod", "idx": idx, "coeffs": coeffs, "mod": mod, "rem": rem}

        if len(set(witness[i] for i in idx)) != len(idx): return None
        return {"type": "alldiff", "idx": idx}

    def _constraint_text(self, c):
        if c["type"] in ("lin", "mod"):
            parts = [(f"x{i}" if a == 1 else f"-x{i}" if a == -1 else f"{a}*x{i}") for a, i in zip(c['coeffs'], c['idx'])]
            expr = " + ".join(parts).replace("+ -", "- ")
            if c["type"] == "lin": return f"{expr} {c['op']} {c['rhs']}"
            return f"({expr}) % {c['mod']} == {c['rem']}"
        return f"AllDifferent({', '.join(f'x{i}' for i in c['idx'])})"

    def _add_base(self, solver, xs, domains, constraints):
        for x, ub in zip(xs, domains): solver.add(x >= 0, x <= ub)
        for c in constraints:
            if c["type"] == "lin":
                expr = Sum([a * xs[i] for a, i in zip(c["coeffs"], c["idx"])])
                if c["op"] == "==": solver.add(expr == c["rhs"])
                elif c["op"] == "!=": solver.add(expr != c["rhs"])
                elif c["op"] == "<=": solver.add(expr <= c["rhs"])
                else: solver.add(expr >= c["rhs"])
            elif c["type"] == "mod":
                solver.add(Sum([a * xs[i] for a, i in zip(c["coeffs"], c["idx"])]) % c["mod"] == c["rem"])
            elif c["type"] == "alldiff":
                solver.add(Distinct(*[xs[i] for i in c["idx"]]))

    def _solve_min(self, domains, constraints):
        xs = [Int(f"x{i}") for i in range(len(domains))]
        opt = Optimize()
        opt.set(priority="lex")
        self._add_base(opt, xs, domains, constraints)
        for x in xs: opt.minimize(x)
        if opt.check() != sat: return None
        return [opt.model().eval(x, model_completion=True).as_long() for x in xs]

    def _solve_all(self, domains, constraints):
        xs = [Int(f"x{i}") for i in range(len(domains))]
        solver = Solver()
        self._add_base(solver, xs, domains, constraints)
        solutions, cap = [], self.config.max_solutions
        while solver.check() == sat:
            sol = [solver.model().eval(x, model_completion=True).as_long() for x in xs]
            solutions.append(sol)
            if cap and len(solutions) > cap: return None, True
            solver.add(Or(*[x != v for x, v in zip(xs, sol)]))
        return sorted(solutions) if solutions else None, False

    def generate(self):
        mode = self.config.model_mode
        if mode == "any":
            mode = random.choices(["attribute", "grid", "linear"], weights=[3, 3, 2])[0]
        return {"attribute": self._generate_attribute, "grid": self._generate_grid}.get(mode, self._generate_linear)()

    def _generate_linear(self):
        rng = self._rng()
        n, max_dom, n_cons = max(2, self.config.n_vars), max(2, self.config.max_domain), max(1, self.config.n_constraints)

        for _ in range(self.config.max_tries):
            # Dynamic structure fallback for pure randomness per instance
            mode = rng.choice(["random", "graph", "grid", "clustered"]) if self.config.structure_mode == "any" else self.config.structure_mode
            neighbors = self._build_neighbors(rng, n, mode)
            domains = [rng.randint(1, max_dom) for _ in range(n)]
            witness = [rng.randint(0, ub) for ub in domains]

            constraints, seen, attempts = [], set(), 0
            while len(constraints) < n_cons and attempts < max(16, 12 * n_cons):
                attempts += 1
                idx = self._sample_scope(rng, neighbors, n, mode)
                if c := self._sample_constraint(rng, idx, witness, self.config.coef_bound):
                    if (key := json.dumps(c, sort_keys=True)) not in seen:
                        seen.add(key); constraints.append(c)

            if len(constraints) < max(1, n_cons // 2): continue

            if rng.random() < self.config.unsat_prob:
                i = rng.randrange(n)
                a = rng.randint(0, domains[i])
                b = rng.choice([x for x in range(domains[i] + 1) if x != a] or [a])
                constraints += [
                    {"type": "lin", "idx": [i], "coeffs": [1], "op": "==", "rhs": a},
                    {"type": "lin", "idx": [i], "coeffs": [1], "op": "==", "rhs": b},
                ]

            solve_mode = self.config.solve_mode.lower()
            if solve_mode in ("all", "lex_all"):
                solution, overflow = self._solve_all(domains, constraints)
                # Fallback to Min if "all" hits bounds
                if overflow:
                    solve_mode, solution = "min", self._solve_min(domains, constraints)
            else:
                solution = self._solve_min(domains, constraints)

            metadata = edict({
                "domains": domains, "constraints": constraints, "solution": solution,
                "solve_mode": solve_mode, "structure_mode": mode, "model_mode": "linear",
                "instance": "Variables/domains:\n" + \
                            "\n".join(f"- 0 <= x{i} <= {ub}" for i, ub in enumerate(domains)) + \
                            "\n\nConstraints:\n" + "\n".join(f"{j+1}. {self._constraint_text(c)}" for j, c in enumerate(constraints))
            })
            return Problem(metadata=metadata, answer="UNSAT" if solution is None else json.dumps(solution))
            
        raise RuntimeError("Failed to generate a CSP instance.")

    def _generate_attribute(self):
        rng = self._rng()
        people = "Alice Bruno Clara David Elena".split()[:max(3, min(5, int(self.config.n_vars) + 2))]
        cats = {
            "color": "red blue green yellow white".split()[:len(people)],
            "pet": "cat dog bird fish horse".split()[:len(people)],
            "drink": "tea milk juice water coffee".split()[:len(people)],
            "snack": "apple bread cake dates eggs".split()[:len(people)],
            "hobby": "chess music art dance tennis".split()[:len(people)],
        }
        sol = {cat: dict(zip(vals, rng.sample(range(len(people)), len(people)))) for cat, vals in cats.items()}
        var = {(cat, val): Int(f"{cat}_{val}") for cat, vals in cats.items() for val in vals}
        base = Solver()
        for cat, vals in cats.items():
            base.add(Distinct(*[var[cat, v] for v in vals]))
            for v in vals: base.add(var[cat, v] >= 0, var[cat, v] < len(people))

        qcat = rng.choice(list(cats))
        qval = rng.choice(cats[qcat])
        answer_idx = sol[qcat][qval]
        k = min(len(cats) - 1, len(people) - 1, max(2, int(self.config.n_constraints) // 2))
        link_cats = rng.sample([c for c in cats if c != qcat], k)
        decoys = rng.sample([i for i in range(len(people)) if i != answer_idx], k)
        clues = []
        for cat in link_cats:
            val = next(v for v in cats[cat] if sol[cat][v] == answer_idx)
            base.add(var[qcat, qval] == var[cat, val])
            clues.append(f"{qval} {qcat} and {val} {cat} belong to the same person.")
        for cat, decoy in zip(link_cats, decoys):
            keep = {answer_idx, decoy}
            for val in cats[cat]:
                if sol[cat][val] not in keep:
                    base.add(var[cat, val] == sol[cat][val])
                    clues.append(f"{val} {cat} belongs to {people[sol[cat][val]]}.")
        ans = self._unique_value(base, var[qcat, qval], range(len(people)))
        if ans is not None:
            answer = people[ans]
            prompt = (
                f"People: {', '.join(people)}.\n"
                f"Each {', '.join(cats)} is used once.\n"
                "Clues:\n" + "\n".join(f"- {c}" for c in clues) +
                f"\n\nWho has the {qval} {qcat}?\nAnswer with one name."
            )
            return Problem(edict(model_mode="attribute", prompt=prompt, clues=clues, query=(qcat, qval), solution=answer), answer)
        raise RuntimeError("Failed to generate an attribute CSP instance.")

    def _generate_grid(self):
        rng = self._rng()
        n = max(3, min(5, int(self.config.n_vars) + 2))
        nums = rng.sample(range(1, n + 1), n)
        sol = [[nums[(r + c) % n] for c in range(n)] for r in range(n)]
        rng.shuffle(sol)
        var = [[Int(f"r{r+1}c{c+1}") for c in range(n)] for r in range(n)]
        base = Solver()
        for row in var:
            base.add(Distinct(*row), *[x >= 1 for x in row], *[x <= n for x in row])
        for c in range(n):
            base.add(Distinct(*[var[r][c] for r in range(n)]))
        qr, qc = rng.randrange(n), rng.randrange(n)
        candidates = []
        for r in range(n):
            for c in range(n):
                if (r, c) != (qr, qc):
                    candidates.append((f"r{r+1}c{c+1} = {sol[r][c]}", var[r][c] == sol[r][c]))
                for dr, dc in ((1, 0), (0, 1)):
                    rr, cc = r + dr, c + dc
                    if rr < n and cc < n:
                        op = "<" if sol[r][c] < sol[rr][cc] else ">"
                        z = var[r][c] < var[rr][cc] if op == "<" else var[r][c] > var[rr][cc]
                        candidates.append((f"r{r+1}c{c+1} {op} r{rr+1}c{cc+1}", z))
        k = min((n + 1) // 2, max(2, int(self.config.n_constraints) // 2))
        ans = sol[qr][qc]
        vals = [v for v in range(1, n + 1) if v != ans]
        row_vals = set(rng.sample(vals, k - 1))
        col_vals = set(rng.sample([v for v in vals if v not in row_vals], k - 1))
        row_hide = {qc} | {c for c in range(n) if sol[qr][c] in row_vals}
        col_hide = {qr} | {r for r in range(n) if sol[r][qc] in col_vals}
        clues = []
        for c in rng.sample([c for c in range(n) if c not in row_hide], n - k):
            base.add(var[qr][c] == sol[qr][c])
            clues.append(f"r{qr+1}c{c+1} = {sol[qr][c]}")
        for r in rng.sample([r for r in range(n) if r not in col_hide], n - k):
            base.add(var[r][qc] == sol[r][qc])
            clues.append(f"r{r+1}c{qc+1} = {sol[r][qc]}")
        rng.shuffle(clues)
        ans = self._unique_value(base, var[qr][qc], range(1, n + 1))
        if ans is not None:
            prompt = (
                f"{n}x{n} grid. Each row and column contains 1..{n} once.\n"
                "Clues:\n" + "\n".join(f"- {c}" for c in clues) +
                f"\n\nWhat is r{qr+1}c{qc+1}?\nAnswer with one number."
            )
            return Problem(edict(model_mode="grid", prompt=prompt, clues=clues, query=(qr + 1, qc + 1), solution=ans), str(ans))
        raise RuntimeError("Failed to generate a grid CSP instance.")

    def prompt(self, metadata):
        if "prompt" in metadata:
            return metadata.prompt
        order = ", ".join(f"x{i}" for i in range(len(metadata['domains'])))
        if metadata.get("solve_mode", "min") == "all":
            return f"{metadata['instance']}\nEnumerate ALL satisfying assignments in variable order [{order}].\nThe answer is a lexicographically sorted Python list of int lists, or UNSAT.\n"
        return f"{metadata['instance']}\nFind the lexicographically smallest satisfying assignment in variable order [{order}].\nThe answer is a Python list of ints, or UNSAT."

    def score_answer(self, answer, entry):
        metadata = entry.metadata if hasattr(entry, "metadata") else entry["metadata"]
        if metadata.get("model_mode") in {"attribute", "grid"}:
            return float(str(answer).strip().lower() == str(entry.answer if hasattr(entry, "answer") else entry["answer"]).strip().lower())
        def _parse(s):
            if not isinstance(s, str) or not (s := s.strip()): return None
            if s.upper() == "UNSAT": return "UNSAT"
            try:
                def norm(v): return [norm(u) for u in v] if isinstance(v, (list, tuple)) else v
                x = norm(ast.literal_eval(s))
                if isinstance(x, list) and (all(type(v) is int for v in x) or all(isinstance(r, list) and all(type(v) is int for v in r) for r in x)):
                    return x
            except Exception: pass
            return None

        parsed = _parse(answer)
        expected = metadata["solution"]
        if expected is None: return float(parsed == "UNSAT")
        if parsed == "UNSAT" or not isinstance(parsed, list): return 0.0
        
        # Validates proper dimensionality match ("all" == 2D array, "min" == 1D array)
        if metadata.get("solve_mode", "min") == "all":
            return float(parsed == expected and (not parsed or isinstance(parsed[0], list)))
        return float(parsed == expected and (not parsed or not isinstance(parsed[0], list)))


if __name__ == "__main__":
    print("=" * 60)
    print("TEST: 'any' mode (Randomly cycles graphs), default 'all' (Fallbacks to 'min')")
    print("=" * 60)
    for _ in range(4):
        cfg = ConstraintSatisfactionConfig(
            n_vars=4,
            max_domain=3,
            n_constraints=5,
            coef_bound=2,
            structure_mode="any",
            solve_mode="all",
            max_solutions=32,
            seed=random.randint(0, 1000)
        )
        task = ConstraintSatisfaction(config=cfg)
        prob = task.generate()
        
        print(f"\n--- Structure chosen: {prob.metadata.structure_mode} ---")
        print(task.prompt(prob.metadata))
        
        sol = json.loads(prob.answer) if prob.answer != "UNSAT" else "UNSAT"
        count = len(sol) if isinstance(sol, list) and sol and isinstance(sol[0], list) else (0 if sol == "UNSAT" else 1)
        print(f"Answer ({count} solutions, solve_mode used={prob.metadata.solve_mode}):\n{prob.answer}\n")
