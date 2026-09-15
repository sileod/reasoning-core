"""Lexicographically canonical subset-minimal inconsistent subset of constraints."""

import random
from dataclasses import dataclass
from itertools import combinations

from z3 import Bool, Not, Or, Solver, sat

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'minimal_unsat_core (draw 1 of 1)',
 'hypothesis': 'HV-051',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/manual_high_value_80_r1/minimal_unsat_core',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1787056888,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class MinimalUnsatCoreConfig(Config):
    nvars: int = 3
    nclauses: int = 4
    max_width: int = 3

    def apply_difficulty(self, level):
        self.nvars = 3 + level // 2
        self.nclauses = 4 + level
        self.max_width = 2 + level // 2


def _check_sat(nvars, clauses):
    solver = Solver()
    for clause in clauses:
        solver.add(Or(*[_lit(v, p) for (v, p) in clause]))
    return solver.check() == sat


def _lit(v, p):
    b = Bool("x%d" % v)
    return b if p else Not(b)


def _minimal_unsat_subsets(nvars, clauses):
    n = len(clauses)
    status = {}
    mus = []
    for size in range(1, n + 1):
        for combo in combinations(range(n), size):
            fs = frozenset(combo)
            ok = _check_sat(nvars, [clauses[i] for i in combo])
            status[fs] = ok
            if not ok:
                if size == 1 or all(status.get(frozenset(combo[:j] + combo[j + 1:]), False)
                                    for j in range(size)):
                    mus.append(combo)
    return mus


def _render_clause(i, clause):
    parts = []
    for (v, p) in sorted(clause, key=lambda t: t[0]):
        parts.append(("x%d" % v) if p else ("not x%d" % v))
    return "C%d: (%s)" % (i + 1, " or ".join(parts))


def _generate(nvars, nclauses, max_width):
    for _ in range(40):
        clauses = []
        for _ in range(nclauses):
            width = random.randint(1, max_width)
            vars_ = random.sample(range(nvars), min(width, nvars))
            clause = [(v, random.random() < 0.5) for v in vars_]
            clauses.append(clause)
        if len(clauses) < 1:
            continue
        if _check_sat(nvars, clauses):
            continue
        mus = _minimal_unsat_subsets(nvars, clauses)
        if not mus:
            continue
        best = min(mus)
        return clauses, best
    raise RuntimeError("could not generate a minimal unsat core")


class MinimalUnsatCore(Task):
    summary = ("Find the lexicographically canonical subset-minimal inconsistent subset "
               "of small Boolean-clause constraints.")
    config_cls = MinimalUnsatCoreConfig

    def generate_entry(self):
        clauses, best = _generate(self.config.nvars, self.config.nclauses,
                                  self.config.max_width)
        sizes = [len(c) for c in clauses]
        answer = " ".join(str(i + 1) for i in best)
        assert self.score_answer(answer,
                                 Entry(metadata={"clauses": clauses, "answer": answer},
                                       answer=answer)) == 1.0
        return Entry(metadata={
            "nvars": int(self.config.nvars),
            "clauses": [[[int(v), bool(p)] for (v, p) in c] for c in clauses],
            "widths": [int(s) for s in sizes],
            "answer": answer,
        }, answer=answer)

    def render_prompt(self, metadata):
        lines = ["Consider the following Boolean constraints over boolean variables "
                 "x0..x%d." % (metadata["nvars"] - 1)]
        for i, clause in enumerate(metadata["clauses"]):
            lines.append(_render_clause(i, clause))
        lines.append(
            "Together these constraints are unsatisfiable. A subset-minimal "
            "inconsistent subset is a set of these constraints that is itself "
            "unsatisfiable but becomes satisfiable if any one of its members is "
            "removed. Give the lexicographically smallest such subset-minimal "
            "inconsistent subset, as a space-separated list of ascending constraint "
            "indices (C1 => 1, C2 => 2, ...). For example the answer format is "
            "'1 3 4'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        if not isinstance(answer, str):
            return 0.0
        try:
            got = tuple(int(x) for x in answer.strip().split())
        except ValueError:
            return 0.0
        want = tuple(int(x) for x in entry.metadata["answer"].split())
        return 1.0 if got == want else 0.0
