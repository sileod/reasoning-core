import random
from dataclasses import dataclass

import sympy

from reasoning_core.template import Config, Entry, Task


@dataclass
class ClusterSeedEvolutionConfig(Config):
    rank: int = 3
    nfrozen: int = 2
    steps: int = 2
    entry_mag: int = 2

    def apply_difficulty(self, level):
        self.rank = min(4, 3 + level // 2)
        self.nfrozen = min(3, 2 + level // 3)
        self.steps = 2 + min(level, 5)
        self.entry_mag = 1 + (level // 3)


def _skew_symmetric_initial(rank, nfrozen, mag):
    rows = rank + nfrozen
    B = [[0] * rank for _ in range(rows)]
    for i in range(rank):
        for j in range(i + 1, rank):
            v = random.randint(1, mag)
            if random.random() < 0.5:
                v = -v
            B[i][j] = v
            B[j][i] = -v
    for fi in range(rank, rows):
        for j in range(rank):
            if random.random() < 0.6:
                B[fi][j] = random.randint(1, mag)
    return B


def _mutate_matrix(B, k):
    R = len(B)
    C = len(B[0])
    Bp = [[0] * C for _ in range(R)]
    for i in range(R):
        for j in range(C):
            if i == k or j == k:
                Bp[i][j] = -B[i][j]
            else:
                Bp[i][j] = B[i][j] + max(B[i][k], 0) * max(B[k][j], 0) - max(-B[i][k], 0) * max(-B[k][j], 0)
    return Bp


def _mutate_variable(exprs, frozen_syms, B, k):
    xk = exprs[k]
    pos = sympy.Integer(1)
    neg = sympy.Integer(1)
    R = len(B)
    for i in range(R):
        b = B[i][k]
        if not b:
            continue
        if i < len(exprs):
            xval = exprs[i]
        else:
            xval = frozen_syms[i - len(exprs)]
        if b > 0:
            pos = pos * xval ** b
        else:
            neg = neg * xval ** (-b)
    new = sympy.cancel((pos + neg) / xk)
    if not (sympy.cancel(new * xk - (pos + neg)) == 0):
        raise RuntimeError("mutation check failed")
    return new


TASK_META = {'parent_source_id': None,
 'idea': 'cluster_seed_evolution (variant 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/cluster_seed_evolution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _canonical(expr, symbols):
    return sympy.together(sympy.cancel(expr))


def _score_rational(answer, gold, symbols):
    if not isinstance(answer, str):
        return 0.0
    try:
        atab = {str(s): s for s in symbols}
        gtab = {str(s): s for s in symbols}
        a = sympy.sympify(answer, locals=atab)
        g = sympy.sympify(gold, locals=gtab)
    except Exception:
        return 0.0
    try:
        ca = _canonical(a, symbols)
        cg = _canonical(g, symbols)
        return 1.0 if sympy.simplify(ca - cg) == 0 else 0.0
    except Exception:
        return 0.0


class ClusterSeedEvolution(Task):
    summary = ("Evolve skew-symmetric exchange matrices and cluster-variable rational expressions through "
               "seed mutations, frozen-variable renames and index relabelings; return a queried cluster variable "
               "as a canonical rational expression in the initial symbols.")
    design_choice = ("Present the initial seed with symbolic frozen variables and require the final answer as "
                     "a rational expression in those symbols, with coefficients extracted canonically.")
    config_cls = ClusterSeedEvolutionConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        rank = cfg.rank
        nfrozen = cfg.nfrozen
        steps = cfg.steps
        mag = cfg.entry_mag

        x_names = ["x%d" % i for i in range(rank)]
        f_names = ["f%d" % j for j in range(nfrozen)]
        x_syms = [sympy.Symbol(n) for n in x_names]
        f_syms = [sympy.Symbol(n) for n in f_names]
        exprs = list(x_syms)
        frozen_syms = list(f_syms)
        mutated = [False] * rank

        B = _skew_symmetric_initial(rank, nfrozen, mag)
        initial_matrix = [[int(c) for c in row] for row in B]
        ops = []
        prev_k = None

        nmut = max(1, min(steps, 1 + rank // 2))
        for s in range(steps):
            if s < nmut:
                typ = "mutate"
            else:
                typ = random.choice(["relabel", "rename"])
            if typ == "mutate":
                k = random.randrange(rank)
                tries = 0
                while tries < 8 and prev_k is not None and k == prev_k:
                    k = random.randrange(rank)
                    tries += 1
                exprs[k] = _mutate_variable(exprs, frozen_syms, B, k)
                B = _mutate_matrix(B, k)
                mutated[k] = True
                prev_k = k
                ops.append(("mutate", k))
            elif typ == "relabel":
                perm = list(range(rank))
                random.shuffle(perm)
                exprs = [exprs[perm[j]] for j in range(rank)]
                mutated = [mutated[perm[j]] for j in range(rank)]
                newB = []
                for i in range(len(B)):
                    src = perm[i] if i < rank else i
                    newB.append(B[src])
                for i in range(rank):
                    newB[i] = [newB[i][perm[j]] for j in range(rank)]
                B = newB
                ops.append(("relabel", list(perm)))
            else:
                j = random.randrange(nfrozen)
                old = frozen_syms[j]
                new_sym = sympy.Symbol("g_%d" % (100 + s))
                exprs = [e.subs(old, new_sym) for e in exprs]
                frozen_syms[j] = new_sym
                ops.append(("rename", str(old), str(new_sym)))

        q = random.choice([i for i, m in enumerate(mutated) if m])
        all_symbols = x_syms + frozen_syms
        gold_expr = _canonical(exprs[q], all_symbols)
        gold = sympy.sstr(gold_expr)

        metadata = {
            "rank": rank,
            "nfrozen": nfrozen,
            "initial_matrix": initial_matrix,
            "x_names": x_names,
            "frozen_names": [str(s) for s in frozen_syms],
            "ops": ops,
            "query_index": q,
            "symbols": [str(s) for s in all_symbols],
            "answer": gold,
        }
        return Entry(metadata=metadata, answer=gold)

    def render_prompt(self, metadata):
        lines = []
        lines.append("We evolve a cluster seed with symbolic frozen variables.")
        lines.append("There are {} mutable variables {} and frozen variables {}.".format(
            metadata["rank"], ", ".join(metadata["x_names"]), ", ".join(metadata["frozen_names"])))
        lines.append("The initial extended exchange matrix B (rows: mutable x's then frozen variables; "
                     "columns: the mutable x's) is:")
        for row in metadata["initial_matrix"]:
            lines.append("  " + " ".join(str(c) for c in row))
        lines.append("Initially each mutable variable x_i equals its own symbol x_i.")
        if metadata["ops"]:
            lines.append("Apply these seed-evolution operations in order:")
            for op in metadata["ops"]:
                if op[0] == "mutate":
                    lines.append("  mutate the seed at mutable index {}".format(op[1]))
                elif op[0] == "relabel":
                    lines.append("  relabel the mutable variables so that new index j holds the variable that "
                                 "was at old index {}".format(", ".join(str(v) for v in op[1])))
                else:
                    lines.append("  rename frozen variable {} to {}".format(op[1], op[2]))
        lines.append("After all operations, report the rational expression (in the stated symbols, fully "
                     "cancelled and with canonical rational coefficients) of the mutable cluster variable "
                     "at current index {}.".format(metadata["query_index"]))
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        md = entry.metadata
        symbols = [sympy.Symbol(n) for n in md["symbols"]]
        return _score_rational(answer, md["answer"], symbols)
