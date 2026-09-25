import random
from dataclasses import dataclass

from sympy import Matrix, Rational, Symbol

from reasoning_core.template import Config, Entry, Task


@dataclass
class BoundaryResponseConfig(Config):
    hidden: int = 2
    max_cond: int = 5
    extra: int = 1

    def apply_difficulty(self, level):
        self.hidden = 2 + 2 * level
        self.max_cond = 3 + 2 * level
        self.extra = 1 + level


def tree_on(nodes):
    """Random tree over the given integer node list (module RNG deterministic)."""
    seen = [nodes[0]]
    edges = []
    for x in nodes[1:]:
        edges.append((x, random.choice(seen)))
        seen.append(x)
    return edges


def build_general(n, extra):
    """Connected graph over nodes 0..n-1; terminals are fixed to 0 and 1."""
    edges = set(tree_on(list(range(n))))
    for _ in range(extra):
        u = random.randrange(n)
        v = random.randrange(n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    return sorted(edges)


def build_split(n, extra):
    """Two halves joined by a single bridge so a known edge separates terminal 0 from terminal 1.

    Side A = {0} + hidden A, side B = {1} + hidden B. Returns (edges, bridge)."""
    for _ in range(50):
        hidden = list(range(2, n))
        if len(hidden) < 2:
            continue
        k = random.randrange(1, len(hidden))
        ha = hidden[:k]
        hb = hidden[k:]
        pA = random.choice(ha)
        pB = random.choice(hb)
        edges = set(tree_on([0] + ha)) | set(tree_on(hb + [1]))
        edges.add((min(pA, pB), max(pA, pB)))
        Anodes = [0] + ha
        Bnodes = hb + [1]
        for _ in range(extra):
            if random.random() < 0.5:
                u, v = random.choice(Anodes), random.choice(Anodes)
            else:
                u, v = random.choice(Bnodes), random.choice(Bnodes)
            if u != v:
                edges.add((min(u, v), max(u, v)))
        return sorted(edges), (min(pA, pB), max(pA, pB))
    raise RuntimeError("build_split failed to build a bridged network")


def assign_conductances(edges, max_cond):
    cond = {}
    for (u, v) in edges:
        cond[(u, v)] = random.randint(1, max_cond)
    return cond


def laplacian(n, cond):
    L = [[Rational(0) for _ in range(n)] for _ in range(n)]
    for (u, v) in cond:
        g = cond[(u, v)]
        L[u][u] += g
        L[v][v] += g
        L[u][v] -= g
        L[v][u] -= g
    return Matrix(L)


def eff_conductance(n, cond, a=0, b=1):
    L = laplacian(n, cond)
    term = [a, b]
    hid = [i for i in range(n) if i != a and i != b]
    LTT = L[term, term]
    LTH = L[term, hid]
    LHT = L[hid, term]
    LHH = L[hid, hid]
    Lred = LTT - LTH * LHH.inv() * LHT
    return -Lred[0, 1]


def rat_str(v):
    r = Rational(v)
    num = abs(int(r.p))
    den = int(r.q)
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def parse_ratio(tok):
    s = str(tok).strip().strip('"').strip("'")
    try:
        return Rational(s)
    except Exception:
        return None


class EffectiveBoundaryResponse(Task):
    summary = ("Eliminate hidden nodes from rational conductance networks via Kron reduction "
               "preserving terminal current-voltage behavior; recover the boundary response "
               "(effective conductance between terminals), decide exterior equivalence of two "
               "networks, or infer a uniquely determined hidden edge conductance that reproduces "
               "a stated boundary response.")
    config_cls = BoundaryResponseConfig

    def _entryA(self, n, max_cond, extra):
        edges = build_general(n, extra)
        cond = assign_conductances(edges, max_cond)
        G = eff_conductance(n, cond)
        gold = rat_str(G)
        return _make_entry(metadata={"mode": "A",
                                     "edges": [(e[0], e[1], int(c)) for e, c in cond.items()],
                                     "n": n,
                                     "gold": gold}, answer=gold), "A"

    def _entryB(self, n, max_cond, extra):
        same = random.random() < 0.5
        e1 = build_general(n, extra)
        c1 = assign_conductances(e1, max_cond)
        G1 = eff_conductance(n, c1)
        if same:
            c2 = dict(c1)
            G2 = G1
        else:
            for _ in range(50):
                e2 = list(e1)
                (u, v) = random.choice(list(c1.keys()))
                c2 = dict(c1)
                c2[(u, v)] = random.randint(1, max_cond)
                G2 = eff_conductance(n, c2)
                if G2 != G1:
                    break
            else:
                raise RuntimeError("mode B could not find unequal network")
        gold = "yes" if G2 == G1 else "no"
        return (_make_entry(metadata={"mode": "B",
                                      "ed1": [(e[0], e[1], int(c)) for e, c in c1.items()],
                                      "ed2": [(e[0], e[1], int(c)) for e, c in c2.items()],
                                      "n": n, "gold": gold}, answer=gold), "B")

    def _entryC(self, n, max_cond, extra):
        edges, bridge = build_split(n, extra)
        cond = assign_conductances(edges, max_cond)
        g0 = cond[bridge]
        target = eff_conductance(n, cond)
        x = Symbol("x")
        cx1 = dict(cond); cx1[bridge] = Rational(1)
        cx2 = dict(cond); cx2[bridge] = Rational(2)
        cx3 = dict(cond); cx3[bridge] = Rational(3)
        G1 = eff_conductance(n, cx1)
        G2 = eff_conductance(n, cx2)
        G3 = eff_conductance(n, cx3)
        M = Matrix([[Rational(1), Rational(1), -G1, -G1],
                    [Rational(2), Rational(1), -2 * G2, -G2],
                    [Rational(3), Rational(1), -3 * G3, -G3]])
        ns = M.nullspace()
        if not ns:
            raise RuntimeError("mode C nullspace empty")
        v = ns[0]
        a, b, c, d = v[0], v[1], v[2], v[3]
        den = a - target * c
        if den == 0:
            raise RuntimeError("mode C division by zero")
        xr = (target * d - b) / den
        xr = Rational(xr)
        # verify uniqueness and reproduction
        cand = dict(cond); cand[bridge] = xr
        if eff_conductance(n, cand) != target or xr <= 0 or Rational(xr) != Rational(g0):
            raise RuntimeError("mode C verification failed")
        shown = []
        for (u, v) in edges:
            if (u, v) == bridge:
                shown.append((u, v, None))
            else:
                shown.append((u, v, int(cond[(u, v)])))
        gold = rat_str(g0)
        return (_make_entry(metadata={"mode": "C",
                                      "edges": shown, "bridge": (bridge[0], bridge[1]),
                                      "target": rat_str(target), "n": n, "gold": gold},
                            answer=gold), "C")

    def generate_entry(self):
        cfg = self.config
        n = cfg.hidden + 2
        for _ in range(20):
            r = random.random()
            try:
                if r < 0.34:
                    e, _ = self._entryA(n, cfg.max_cond, cfg.extra)
                elif r < 0.67:
                    e, _ = self._entryB(n, cfg.max_cond, cfg.extra)
                else:
                    e, _ = self._entryC(n, cfg.max_cond, cfg.extra)
                return e
            except (RuntimeError, ZeroDivisionError):
                continue
        raise RuntimeError("could not generate a valid entry")

    def render_prompt(self, metadata):
        mode = metadata["mode"]
        if mode == "A":
            parts = [f"(({u},{v}):{g})" for (u, v, g) in metadata["edges"]]
            body = "A resistive network has terminals 0 and 1 and hidden interior nodes. " \
                   "Edge conductances in siemens are: " + ", ".join(parts) + "."
            return body + (" Current-voltage behavior at the terminals is fully given by the "
                           "effective conductance between terminals 0 and 1. Eliminate every "
                           "hidden node (Kron reduction, Schur complement) while preserving "
                           "terminal behavior and give the resulting effective conductance "
                           "between terminals 0 and 1. Answer with one rational number in "
                           "lowest terms, e.g. 3/7.")
        if mode == "B":
            p1 = [f"(({u},{v}):{g})" for (u, v, g) in metadata["ed1"]]
            p2 = [f"(({u},{v}):{g})" for (u, v, g) in metadata["ed2"]]
            return ("Two resistive networks share terminals 0 and 1 with hidden interior nodes. "
                    "Network one conductances: " + ", ".join(p1) + ". Network two conductances: "
                    + ", ".join(p2) + ". Two networks are exterior-equivalent if their terminal "
                    "current-voltage behavior is identical, i.e. the effective conductance between "
                    "terminals 0 and 1 is the same after eliminating all hidden nodes. Are they "
                    "exterior-equivalent? Answer yes or no.")
        p = [f"(({u},{v}):{g})" if g is not None else f"(({u},{v}):e)"
             for (u, v, g) in metadata["edges"]]
        gx, gy = metadata["bridge"]
        return ("A resistive network has terminals 0 and 1 and hidden interior nodes. One edge "
                f"({gx},{gy}) has unknown conductance e, all other conductances in siemens are: "
                + ", ".join(p) + ". Eliminating all hidden nodes preserves terminal "
                "current-voltage behavior, whose effective conductance between terminals 0 and 1 "
                f"must equal {metadata['target']}. The unknown conductance is uniquely "
                "determined by this boundary response. Give the value of e. Answer with one "
                "rational number in lowest terms, e.g. 3/7.")

    def score_answer(self, answer, entry):
        mode = entry.metadata["mode"]
        gold = entry.metadata["gold"]
        if mode == "B":
            a = str(answer).strip().lower()
            return 1.0 if a == gold else 0.0
        gr = parse_ratio(gold)
        ar = parse_ratio(answer)
        if gr is None or ar is None:
            return 0.0
        return 1.0 if ar == gr else 0.0


def _make_entry(metadata, answer):
    return Entry(metadata=metadata, answer=answer)


TASK_META = {'parent_source_id': None,
 'idea': 'effective_boundary_response (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_invariants_r4/effective_boundary_response',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4238614268,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
