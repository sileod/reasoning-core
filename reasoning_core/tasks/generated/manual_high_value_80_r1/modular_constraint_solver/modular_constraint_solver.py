import random
import re

from dataclasses import dataclass

from sympy.ntheory.modular import solve_congruence

from reasoning_core.template import Task, Entry, Config, edict, render_payload, stochastic_rounding as sround

TASK_META = {'parent_source_id': None,
 'idea': 'modular_constraint_solver (draw 1 of 1)',
 'hypothesis': 'HV-061',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/manual_high_value_80_r1/modular_constraint_solver',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3715178603,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _norm(s):
    return re.sub(r"\s+", "", str(s).strip()).strip().lower()


def _make_consistent(n_cong, min_mod, max_mod, x_range):
    """Build a satisfiable system from a hidden solution x0."""
    x0 = random.randint(0, x_range - 1)
    while True:
        moduli = [random.randint(min_mod, max_mod) for _ in range(n_cong)]
        residues = [x0 % m for m in moduli]
        sol = solve_congruence(*[(a, m) for a, m in zip(residues, moduli)])
        if sol is not None:
            return residues, moduli, int(sol[0]), int(sol[1])


def _make_inconsistent(n_cong, min_mod, max_mod):
    """Build an unsatisfiable system (generalized CRT fails)."""
    for _ in range(500):
        moduli = [random.randint(min_mod, max_mod) for _ in range(n_cong)]
        residues = [random.randint(0, m - 1) for m in moduli]
        if solve_congruence(*[(a, m) for a, m in zip(residues, moduli)]) is None:
            return residues, moduli
    raise RuntimeError("could not construct inconsistent system")


@dataclass
class ModularConstraintSolverConfig(Config):
    n_cong: int = 3
    min_mod: int = 2
    max_mod: int = 20
    x_range: int = 200

    def apply_difficulty(self, level):
        self.n_cong = int(sround(self.n_cong + level))
        self.min_mod = 2
        self.max_mod = int(sround(self.max_mod + level * 15))
        self.x_range = int(sround(self.x_range + level * 400))


class ModularConstraintSolver(Task):
    summary = ("Combine modular congruence constraints including non-coprime moduli, "
               "returning inconsistency or the canonical residue and modulus solution.")

    config_cls = ModularConstraintSolverConfig

    def generate_entry(self):
        c = self.config
        n_cong = int(c.n_cong)
        min_mod = int(c.min_mod)
        max_mod = int(c.max_mod)
        x_range = int(c.x_range)

        consistent = random.random() < 0.8
        if consistent:
            residues, moduli, sol, M = _make_consistent(n_cong, min_mod, max_mod, x_range)
            assert 0 <= sol < M
            assert solve_congruence(*[(a, m) for a, m in zip(residues, moduli)]) == (sol, M)
            answer = "%d mod %d" % (sol, M)
        else:
            residues, moduli = _make_inconsistent(n_cong, min_mod, max_mod)
            assert solve_congruence(*[(a, m) for a, m in zip(residues, moduli)]) is None
            answer = "inconsistent"

        congruences = ["%d mod %d" % (r, m) for r, m in zip(residues, moduli)]
        metadata = edict({
            "congruences": congruences,
            "n_cong": n_cong,
            "consistent": bool(consistent),
            "answer": answer,
        })
        metadata.payload = {"congruences": congruences}
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = "\n".join("x = %s" % s for s in metadata.payload["congruences"])
        return (
            "We are solving for an integer x that must satisfy every congruence below "
            "simultaneously. Each line 'x = a mod m' means x leaves remainder a when "
            "divided by m (that is, x = a + k*m for some integer k). The moduli need not "
            "be pairwise coprime, so combine them with the generalized Chinese Remainder "
            "Theorem: the system is consistent iff for every overlapping modulus pair the "
            "residues agree modulo their greatest common divisor, and then the full "
            "solution set is a single residue class modulo the least common multiple of "
            "all the moduli.\n"
            "Constraints:\n%s\n\n"
            "If the system has no solution, answer with exactly: inconsistent\n"
            "Otherwise answer with the canonical solution as 'R mod M', where R is the "
            "smallest non-negative integer satisfying the system and M is the least "
            "common multiple of all the moduli. For example, a system solved by x = 8 "
            "with modulus 12 is answered '8 mod 12'.\n"
            "The answer is one line."
        ) % lines

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        if _norm(answer) == "":
            return 0.0
        return 1.0 if _norm(answer) == _norm(entry.answer) else 0.0
