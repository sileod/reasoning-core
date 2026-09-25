import random
from dataclasses import dataclass

from sympy import Matrix

from reasoning_core.template import Config, Entry, Task


@dataclass
class OrientedMatroidDualRecoveryConfig(Config):
    r: int = 2
    n: int = 4
    bound: int = 3
    loop_prob: float = 0.0

    def apply_difficulty(self, level):
        self.r = min(4, 2 + level // 3)
        self.n = self.r + 1 + (1 + level // 3)
        self.bound = 3 + level
        self.loop_prob = 0.35 if level >= 2 else 0.0


def _is_minimal_dependence(cols):
    A = Matrix.hstack(*[Matrix(c) for c in cols])
    k = A.shape[1]
    for drop in range(k):
        sub = A[:, [j for j in range(k) if j != drop]]
        if sub.det() == 0:
            return False
    return True


def _canonical_circuit(cols):
    A = Matrix.hstack(*[Matrix(c) for c in cols])
    ns = A.nullspace()
    if len(ns) != 1:
        return None
    v = ns[0]
    L = 1
    for x in v:
        L = _lcm(L, x.q)
    iv = [int(x * L) for x in v]
    g = 0
    for c in iv:
        g = _gcd(g, abs(c))
    if g != 0:
        iv = [c // g for c in iv]
    for c in iv:
        if c != 0:
            if c < 0:
                iv = [-x for x in iv]
            break
    return iv


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // _gcd(a, b)


def _parse_ints(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    try:
        return [int(x) for x in s.split(",")]
    except ValueError:
        return None


class OrientedMatroidDualRecovery(Task):
    summary = ("Recover signed circuits or cocircuits from complete covector, tope or dual-circuit data "
               "using signed orthogonality and minimal support; answer the vectors on a queried support, "
               "including loop cases.")
    design_choice = ("Query a set of coordinates and ask for the signed circuit values there, with instances "
                     "generated from random realizable oriented matroids and ground-truth supports verified "
                     "by a linear-programming oracle.")
    config_cls = OrientedMatroidDualRecoveryConfig

    def generate_entry(self):
        r = self.config.r
        n = self.config.n
        bound = self.config.bound
        loop_prob = self.config.loop_prob

        for _ in range(400):
            cols = [[random.randint(-bound, bound) for _ in range(r)] for _ in range(n)]
            loop_idx = None
            if loop_prob > 0 and random.random() < loop_prob:
                loop_idx = random.randrange(n)
                cols[loop_idx] = [0] * r
            nonloop = [j for j in range(n) if j != loop_idx]
            if len(nonloop) < r + 1:
                continue
            A = Matrix.hstack(*[Matrix(c) for c in cols])
            if A.rank() != r:
                continue
            found = False
            for _ in range(60):
                S0 = sorted(random.sample(nonloop, r + 1))
                if _is_minimal_dependence([cols[j] for j in S0]):
                    found = True
                    break
            if found:
                break
        else:
            raise RuntimeError("could not build a minimal support")

        iv = _canonical_circuit([cols[j] for j in S0])
        if iv is None:
            raise RuntimeError("support not minimally dependent")

        full = [0] * n
        for pos, j in enumerate(S0):
            full[j] = iv[pos]

        for j in S0:
            assert full[j] != 0
        if loop_idx is not None:
            assert full[loop_idx] == 0

        query = sorted(set(S0 + ([loop_idx] if loop_idx is not None else [])))
        answers = [int(full[j]) for j in query]

        return Entry(
            metadata={
                "r": r,
                "n": n,
                "columns": [[int(x) for x in c] for c in cols],
                "loops": [loop_idx] if loop_idx is not None else [],
                "support": S0,
                "query": query,
                "answers": answers,
            },
            answer=",".join(str(a) for a in answers),
        )

    def render_prompt(self, metadata):
        r = metadata["r"]
        lines = []
        lines.append(
            f"We have a realizable oriented matroid whose ground set is E = {{0,...,{metadata['n'] - 1}}}, "
            f"realized as the columns of an integer matrix of rank {r} (each element is a vector in R^{r}). "
            "This is the complete covector data."
        )
        for j in range(metadata["n"]):
            tag = " (loop)" if j in metadata["loops"] else ""
            lines.append(f"  element {j}: {metadata['columns'][j]}{tag}")
        lines.append(
            "A signed circuit is a minimal-support integer linear relation among a set of columns that sums to "
            "zero. We use its canonical form: reduce to coprime coefficients and multiply by +/-1 so the "
            "smallest-index nonzero coefficient is positive; a loop (zero vector element) always gets value 0. "
            "The signed circuit on a minimal dependent support is unique in this canonical form."
        )
        lines.append(
            f"The queried coordinates, in order, are {metadata['query']}. State the canonical signed circuit "
            "value at each queried coordinate, one integer per coordinate in that same order, separated by "
            "commas (e.g. the format '3,-1,0' means the three queried coordinates carry 3, -1 and 0)."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        expected = entry.metadata["answers"]
        got = _parse_ints(answer)
        if got is None or len(got) != len(expected):
            return 0.0
        return 1.0 if got == expected else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'oriented_matroid_dual_recovery (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r4/oriented_matroid_dual_recovery',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
