import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ZigzagCycleSurvivalConfig(Config):
    V: int = 3
    L: int = 4
    baseE: int = 3
    seed: int = 0

    def apply_difficulty(self, level):
        self.V = stochastic_rounding(3 + level)
        self.L = stochastic_rounding(4 + 1.5 * level)
        self.baseE = stochastic_rounding(3 + 1.3 * level)


def _rank_mod_p(mat, p):
    rows = [list(r) for r in mat]
    m = len(rows)
    n = len(rows[0]) if m else 0
    r = 0
    for c in range(n):
        sel = None
        for i in range(r, m):
            if rows[i][c] % p:
                sel = i
                break
        if sel is None:
            continue
        rows[r], rows[sel] = rows[sel], rows[r]
        piv = rows[r][c] % p
        inv = pow(piv, p - 2, p)
        for i in range(m):
            if i != r and (rows[i][c] % p):
                f = rows[i][c] % p
                rows[i] = [(a - f * inv * b) % p for (a, b) in zip(rows[i], rows[r])]
        r += 1
        if r == m:
            break
    return r


def _h1dim(ids, eb, V, p):
    E = len(ids)
    if E == 0:
        return 0
    mat = [eb[i] for i in ids]
    return E - _rank_mod_p(mat, p)


def _barcode(ranks, L):
    ints = []
    b = None
    for t in range(L):
        if ranks[t] == 1 and b is None:
            b = t
        elif ranks[t] == 0 and b is not None:
            ints.append((b, t))
            b = None
    if b is not None:
        ints.append((b, "inf"))
    return ints


def _gen(cfg):
    V = cfg.V
    L = cfg.L
    baseE = cfg.baseE
    if baseE < 0:
        baseE = 0
    field = random.choice((2, 3))
    eb = {}
    nextid = 0
    present = set()
    seq = []

    def boundary():
        return [random.randrange(field) for _ in range(V)]

    guard = 0
    while len(present) < baseE and guard < 400:
        guard += 1
        b = boundary()
        if all(x == 0 for x in b):
            continue
        i = nextid
        nextid += 1
        eb[i] = b
        if _h1dim(list(present) + [i], eb, V, field) > 1:
            continue
        present.add(i)

    stages = [set(present)]
    seq_ops = []
    for _ in range(L - 1):
        added = False
        for attempt in range(50):
            if present and random.random() < 0.45:
                op = "del"
            else:
                op = "add"
            if op == "add":
                b = boundary()
                if all(x == 0 for x in b):
                    continue
                i = nextid
                nextid += 1
                eb[i] = b
                if _h1dim(list(present) + [i], eb, V, field) <= 1:
                    present.add(i)
                    seq_ops.append(("add", i))
                    added = True
                    break
            else:
                i = random.choice(sorted(present))
                present.remove(i)
                seq_ops.append(("del", i))
                added = True
                break
        if not added and present:
            i = random.choice(sorted(present))
            present.remove(i)
            seq_ops.append(("del", i))
        stages.append(set(present))

    ranks = [_h1dim(sorted(s), eb, V, field) for s in stages]
    intervals = _barcode(ranks, L)
    _verify(stages, ranks, intervals, V, field, eb)
    answer = _format_intervals(intervals)
    edge_table = sorted([(i, eb[i]) for i in eb])
    return {
        "field": field,
        "V": V,
        "L": L,
        "edges": edge_table,
        "seq": seq_ops,
        "stage_edges": [sorted(s) for s in stages],
        "ranks": ranks,
        "intervals": intervals,
        "answer": answer,
    }


def _verify(stages, ranks, intervals, V, field, eb):
    if len(ranks) != len(stages):
        raise RuntimeError("rank/stage length mismatch")
    for r in ranks:
        if r not in (0, 1):
            raise RuntimeError("cycle rank not in {0,1}")
    covered = {}
    for (b, d) in intervals:
        for t in range(b, d if isinstance(d, int) else len(stages)):
            if t in covered:
                raise RuntimeError("overlapping intervals")
            covered[t] = True
    for t, r in enumerate(ranks):
        if (r == 1) != (t in covered):
            raise RuntimeError("interval coverage disagrees with rank trajectory")
    for t, s in enumerate(stages):
        if _h1dim(sorted(s), eb, V, field) != ranks[t]:
            raise RuntimeError("rank recomputation mismatch")


def _format_intervals(intervals):
    return ",".join("({0},{1})".format(b, d) for (b, d) in intervals)


def _parse_intervals(text):
    if not isinstance(text, str):
        return None
    pat = re.compile(r"\(\s*(\d+)\s*,\s*(\d+|inf)\s*\)")
    out = []
    for m in pat.finditer(text):
        b = int(m.group(1))
        d = m.group(2)
        if d == "inf":
            out.append((b, "inf"))
        else:
            out.append((b, int(d)))
    return out


class ZigzagCycleSurvival(Task):
    summary = (
        "Track homology classes through an F2/F3 cellular zigzag of 1-cells given by "
        "explicit boundary vectors - classes are born, become boundaries, and later "
        "reopen - and return the dimension-1 persistence birth/death intervals as "
        "canonical comma-separated (b,d) pairs."
    )
    design_choice = (
        "Present the filtration as a list of cell additions/deletions with explicit "
        "boundary matrices, and ask for the persistence intervals as canonical "
        "comma-separated pairs."
    )
    config_cls = ZigzagCycleSurvivalConfig

    def generate_entry(self):
        cfg = self.config
        for _ in range(100):
            data = _gen(cfg)
            if data["intervals"]:
                break
        else:
            raise RuntimeError("could not produce an instance with intervals")
        metadata = {
            "field": data["field"],
            "V": data["V"],
            "L": data["L"],
            "edges": data["edges"],
            "seq": data["seq"],
            "stage_edges": data["stage_edges"],
            "ranks": data["ranks"],
            "intervals": data["intervals"],
        }
        return Entry(metadata=metadata, answer=data["answer"])

    def render_prompt(self, metadata):
        field = metadata["field"]
        V = metadata["V"]
        edges = metadata["edges"]
        lines = []
        lines.append(
            "We track a zigzag filtration of chain complexes over the field F{0} "
            "(all arithmetic below is mod {0}). The complex has vertices "
            "v0, ..., v{1}, all present throughout. It evolves only by adding or "
            "removing 1-cells (edges); each edge carries an explicit boundary, a "
            "formal sum of vertices with coefficients in F{0}.".format(
                field, V - 1
            )
        )
        lines.append("")
        lines.append("Edge boundaries (each is its row in the boundary matrix):")
        for (i, b) in edges:
            term = " + ".join(
                "{0}*v{1}".format(c, j) for (j, c) in enumerate(b) if c % field != 0
            )
            term = term or "0"
            lines.append("e{0}: d(e{0}) = {1}".format(i, term))
        lines.append("")
        lines.append("Filtration (stage 0 onward; under each stage are its present edges):")
        for t, es in enumerate(metadata["stage_edges"]):
            names = ", ".join("e{0}".format(i) for i in es) if es else "(none)"
            lines.append("S{0}: {1}".format(t, names))
        lines.append("")
        lines.append(
            "A homology class (cycle) in dimension 1 is a 1-chain whose boundary is "
            "zero, taken modulo boundaries of higher cells. Its dimension-1 Betti "
            "number at a stage equals (number of present edges) minus the rank of the "
            "boundary matrix over F{0}. Compute the dimension-1 zigzag persistence: "
            "each maximal consecutive run of stages with Betti number 1 is one "
            "interval, born at the first stage of the run and dead at the first "
            "following stage with Betti number 0; a run reaching the last stage is "
            "written with death 'inf'.".format(field)
        )
        lines.append("")
        lines.append(
            "Give only the intervals as comma-separated pairs in order of birth, each "
            "pair as (birth,death), e.g. `(1,3),(5,7)`. Output nothing else."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str) or answer.strip() == "":
            return 0.0
        gold = [(b, d) for (b, d) in entry.metadata["intervals"]]
        user = _parse_intervals(answer)
        if user is None:
            return 0.0
        if len(user) != len(gold):
            return 0.0
        for (gb, gd), (ub, ud) in zip(gold, user):
            if ub != gb:
                return 0.0
            if isinstance(gd, int):
                if ud != gd:
                    return 0.0
            elif ud != "inf":
                return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'zigzag_cycle_survival (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/zigzag_cycle_survival',
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
