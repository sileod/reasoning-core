"""Scissors congruence of given polyhedra decided from volume and Dehn tensor.

By the Dehn--Sydler theorem two polyhedra are scissors congruent exactly when they
have the same volume and the same Dehn invariant, where the Dehn invariant is the
tensor sum over edges of (edge length) ^ (dihedral angle) reduced over the
rationals (an angle class that is a rational multiple of pi is 0). Each
polyhedron is characterized by its volume and the list of its edges' lengths and
dihedral angles, each angle written as an integer combination of the two
independent angle units alpha and beta. The reduced invariant is the pair
(sum len*coeff_alpha, sum len*coeff_beta). The task asks, per given pair of
polyhedra, whether they are scissors congruent.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'scissors_congruence_obstruction (variant 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r4/scissors_congruence_obstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3020341981,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class ScissorsCongruenceConfig(Config):
    pairs_min: int = 2
    pairs_max: int = 3
    edges_min: int = 3
    edges_max: int = 6

    def apply_difficulty(self, level):
        self.pairs_min = 2 + level // 2
        self.pairs_max = 3 + level // 2
        self.edges_min = 3 + level // 2
        self.edges_max = 6 + level // 2


def _reduce(edges):
    ra = sum(L * qa for L, qa, qb in edges)
    rb = sum(L * qb for L, qa, qb in edges)
    return (ra, rb)


def _render_angle(qa, qb):
    if qa == 0 and qb == 0:
        return "0"
    terms = []
    if qa != 0:
        terms.append((qa, "alpha"))
    if qb != 0:
        terms.append((qb, "beta"))
    out = ""
    for v, unit in terms:
        neg = v < 0
        mag = "" if abs(v) == 1 else str(abs(v))
        if not out:
            out = ("-" if neg else "") + mag + unit
        else:
            out += ("-" if neg else "+") + mag + unit
    return out


def _edges_text(edges):
    return ", ".join(
        "length %d at angle %s" % (L, _render_angle(qa, qb))
        for L, qa, qb in edges
    )


def _gen_edges(level, cfg):
    m = random.randint(cfg.edges_min, cfg.edges_max)
    edges = []
    for _ in range(m):
        L = random.randint(1, 6)
        qa = random.randint(0, 2)
        qb = random.randint(0, 2)
        if qa == 0 and qb == 0:
            qa = 1
        edges.append((L, qa, qb))
    if random.random() < 0.5:
        Lc = random.randint(1, 5)
        ca = random.randint(1, 2)
        cb = random.randint(0, 2)
        edges.append((Lc, ca, cb))
        edges.append((Lc, -ca, -cb))
    return edges


def _regroup(edges):
    new = []
    for (L, qa, qb) in edges:
        if L >= 2 and random.random() < 0.4:
            L1 = random.randint(1, L - 1)
            new.append((L1, qa, qb))
            new.append((L - L1, qa, qb))
        else:
            new.append((L, qa, qb))
    random.shuffle(new)
    return new


def _vary_angle(edges):
    new = list(edges)
    idx = random.randrange(len(new))
    L, qa, qb = new[idx]
    while True:
        na = random.randint(-2, 2)
        nb = random.randint(-2, 2)
        if (na, nb) != (qa, qb):
            break
    new[idx] = (L, na, nb)
    random.shuffle(new)
    return new


def _gen_pair(level, cfg):
    edgesA = _gen_edges(level, cfg)
    volA = sum(L for L, _, _ in edgesA)
    redA = _reduce(edgesA)
    flag = random.choice(("Y", "N"))
    if flag == "Y":
        for _ in range(200):
            edgesB = _regroup(edgesA)
            if _reduce(edgesB) == redA:
                break
        volB = sum(L for L, _, _ in edgesB)
        redB = redA
    else:
        for _ in range(200):
            edgesB = _vary_angle(edgesA)
            if _reduce(edgesB) != redA:
                break
        volB = sum(L for L, _, _ in edgesB)
        redB = _reduce(edgesB)
    return flag, edgesA, edgesB, volA, volB, redA, redB


class ScissorsCongruenceObstruction(Task):
    summary = "Decide scissors congruence of polyhedra from volumes and exact edge-length and dihedral-angle bases; reduce global tensor invariants, including cancellations across unequal edge types."
    config_cls = ScissorsCongruenceConfig
    design_choice = "Answer is a short canonical tuple of independent yes/no flags, one per given polyhedron pair, with each flag balanced and instances varying in the number of pairs."

    def generate_entry(self):
        cfg = self.config
        k = random.randint(cfg.pairs_min, cfg.pairs_max)
        flags = []
        pairs = []
        for _ in range(k):
            flag, edgesA, edgesB, volA, volB, redA, redB = _gen_pair(cfg.level, cfg)
            flags.append(flag)
            pairs.append({
                "edgesA": edgesA, "volA": int(volA),
                "edgesB": edgesB, "volB": int(volB),
                "redA": redA, "redB": redB,
            })
        metadata = {"k": int(k), "pairs": pairs}
        return Entry(metadata=metadata, answer="".join(flags))

    def render_prompt(self, metadata):
        m = metadata
        k = m["k"]
        L = []
        L.append("Two polyhedra are scissors congruent when they can be cut into finitely many pieces that can be rearranged into each other. By the Dehn-Sydler theorem this holds exactly when they have the same volume and the same Dehn invariant. The Dehn invariant is the tensor sum over edges of (edge length) tensored with (dihedral angle), reduced over the rationals: an angle that is a rational multiple of pi is treated as 0. Here each dihedral angle is written as an integer combination of the two independent angle units alpha and beta, so the reduced invariant of a polyhedron is the pair (sum over edges of length times alpha-coefficient, sum over edges of length times beta-coefficient). Equal volume and equal reduced invariant means the two polyhedra are scissors congruent; a difference in either means they are not.")
        L.append("Each polyhedron is described by its volume and the list of its edges, each edge giving its length and its dihedral angle.")
        L.append("")
        L.append(f"There are {k} pairs of polyhedra below.")
        for i in range(k):
            p = m["pairs"][i]
            L.append("")
            L.append(f"Pair {i+1}:")
            L.append(f"Polyhedron A: volume {p['volA']}; edges: {_edges_text(p['edgesA'])}.")
            L.append(f"Polyhedron B: volume {p['volB']}; edges: {_edges_text(p['edgesB'])}.")
        L.append("")
        L.append(f"Decide, for each of the {k} pairs in the order they are given, whether the two polyhedra are scissors congruent. Answer with a single string of exactly {k} characters made only of Y and N, the i-th character being Y if pair i is congruent and N otherwise (three pairs that are congruent, not congruent, and not congruent would be YNN). Give only this flag string.")
        return "\n".join(L)

    def score_answer(self, answer, entry):
        return _score_flags(answer, entry.answer)


def _score_flags(answer, gold):
    norm = _normalize_flags(answer, len(gold))
    if norm is None:
        return 0.0
    return 1.0 if norm == gold.upper() else 0.0


def _normalize_flags(raw, k):
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s:
        return None
    toks = s.replace(",", " ").split()
    if len(toks) == 1 and len(toks[0]) == k and all(c.lower() in "yn" for c in toks[0]):
        return toks[0].upper()
    if len(toks) != k:
        return None
    res = []
    for t in toks:
        tl = t.strip().lower()
        if tl in ("y", "yes"):
            res.append("Y")
        elif tl in ("n", "no"):
            res.append("N")
        else:
            return None
    return "".join(res)
