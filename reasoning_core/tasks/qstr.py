import random
from dataclasses import dataclass
from itertools import product
from collections import defaultdict, deque
from z3 import Distinct, Int, Solver, sat

from reasoning_core.template import Task, Problem, Config, edict, stochastic_rounding as sround

# ---- Core types ---------------------------------------------------------

@dataclass(frozen=True)
class Calculus:
    name: str
    base: frozenset
    converse: dict
    compose: dict   # (r1, r2) -> frozenset(base)

# ---- Sound derivation: enumerate, verify saturation --------------------

def _build(domain, rel):
    dom = list(domain)
    n = len(dom)
    R = [[rel(dom[i], dom[j]) for j in range(n)] for i in range(n)]
    cv, cp, seen = {}, defaultdict(set), set()
    for i in range(n):
        Ri = R[i]
        for j in range(n):
            rij = Ri[j]
            cv[rij] = R[j][i]
            seen.add(rij)
            Rj = R[j]
            for k in range(n):
                cp[rij, Rj[k]].add(Ri[k])
    return seen, cv, cp

def derive(name, enum, rel, N):
    """Enumerate over enum(N); confirm fixpoint by rebuilding at enum(N+1).
    If the assertion fires, the table grew — bump N until it stabilises."""
    s1, _,   cp1 = _build(enum(N),     rel)
    s2, cv2, cp2 = _build(enum(N + 1), rel)
    assert s1 == s2,   f"{name}: base relations grew N={N}->{N+1}; bump N"
    assert cp1 == cp2, f"{name}: compose table grew N={N}->{N+1}; bump N"
    return Calculus(name, frozenset(s2), dict(cv2),
                    {k: frozenset(v) for k, v in cp2.items()})

def derive_product(name, calc):
    """Cartesian product of `calc` with itself. Sound when the two factor
    dimensions are independently realisable in the runtime domain (true for
    axis-aligned boxes: x and y can be chosen freely)."""
    base = frozenset((r1, r2) for r1 in calc.base for r2 in calc.base)
    cv = {(a, b): (calc.converse[a], calc.converse[b]) for (a, b) in base}
    cp = {}
    U = calc.base
    for (a1, b1) in base:
        for (a2, b2) in base:
            cp[(a1, b1), (a2, b2)] = frozenset(
                (x, y)
                for x in calc.compose.get((a1, a2), U)
                for y in calc.compose.get((b1, b2), U))
    return Calculus(name, base, cv, cp)

# ---- Path-consistency (sound; not complete on full Allen, which only
#      affects rejection rate, not the validity of accepted singletons) --

def closure(calc, n, hard):
    U = calc.base
    R = {(i, j): U for i in range(n) for j in range(n) if i != j}
    for (i, j), s in hard.items():
        R[i, j] = R[i, j] & s
        R[j, i] = R[j, i] & frozenset(calc.converse[r] for r in s)
        if not R[i, j]:
            return None
    changed = True
    while changed:
        changed = False
        for i, j, k in product(range(n), repeat=3):
            if i == j or j == k or i == k:
                continue
            comp = frozenset().union(*(
                calc.compose.get((r1, r2), U)
                for r1 in R[i, j] for r2 in R[j, k]))
            new = R[i, k] & comp
            if not new:
                return None
            if new != R[i, k]:
                R[i, k] = new
                changed = True
    return R

# ---- Concrete semantics: intervals on [-N, N] (symmetric => nesting) ---

def all_intervals(N):
    pts = range(-N, N + 1)
    return [(a, b) for a in pts for b in pts if a < b]

def all_boxes(N):
    iv = all_intervals(N)
    return [(x0, x1, y0, y1) for (x0, x1) in iv for (y0, y1) in iv]

def allen(a, b):
    sgn = lambda x, y: (x > y) - (x < y)
    return (sgn(a[0], b[0]), sgn(a[0], b[1]),
            sgn(a[1], b[0]), sgn(a[1], b[1]))

def hdir(a, b): return allen((a[0], a[1]), (b[0], b[1]))
def vdir(a, b): return allen((a[2], a[3]), (b[2], b[3]))

def rcc8_iv(a, b):
    """RCC8 on 1D intervals — used for derivation. The composition table is
    dimension-independent, so this table holds for 2D boxes at runtime."""
    a0, a1 = a; b0, b1 = b
    if a1 <  b0 or b1 <  a0:                              return 'DC'
    if a1 == b0 or b1 == a0:                              return 'EC'
    if a == b:                                            return 'EQ'
    if b0 < a0 and a1 < b1:                               return 'NTPP'
    if a0 < b0 and b1 < a1:                               return 'NTPPi'
    if (a0 == b0 and a1 < b1) or (b0 < a0 and a1 == b1): return 'TPP'
    if (a0 == b0 and b1 < a1) or (a0 < b0 and a1 == b1): return 'TPPi'
    return 'PO'

def rcc8_box(a, b):
    """RCC8 on 2D axis-aligned boxes — runtime ground truth."""
    ax0, ax1, ay0, ay1 = a
    bx0, bx1, by0, by1 = b
    cx_lo, cx_hi = max(ax0, bx0), min(ax1, bx1)
    cy_lo, cy_hi = max(ay0, by0), min(ay1, by1)
    if cx_lo >  cx_hi or cy_lo >  cy_hi: return 'DC'
    if cx_lo == cx_hi or cy_lo == cy_hi: return 'EC'
    if a == b: return 'EQ'
    a_in = bx0 <= ax0 and ax1 <= bx1 and by0 <= ay0 and ay1 <= by1
    b_in = ax0 <= bx0 and bx1 <= ax1 and ay0 <= by0 and by1 <= ay1
    tan  = (ax0 == bx0 or ax1 == bx1 or ay0 == by0 or ay1 == by1)
    if a_in: return 'TPP'  if tan else 'NTPP'
    if b_in: return 'TPPi' if tan else 'NTPPi'
    return 'PO'

def coarse_iv(a, b):
    if a[1] <  b[0]: return 'before'
    if b[1] <  a[0]: return 'after'
    return 'overlap'

def cardinal_box(a, b):
    return (coarse_iv((a[0], a[1]), (b[0], b[1])),
            coarse_iv((a[2], a[3]), (b[2], b[3])))

# ---- Labels -------------------------------------------------------------

ALLEN_NAMES = {
    (-1,-1,-1,-1): 'before',       (-1,-1, 0,-1): 'meets',
    (-1,-1, 1,-1): 'overlaps',     (-1,-1, 1, 0): 'finished-by',
    (-1,-1, 1, 1): 'contains',     ( 0,-1, 1,-1): 'starts',
    ( 0,-1, 1, 0): 'equals',       ( 0,-1, 1, 1): 'started-by',
    ( 1,-1, 1,-1): 'during',       ( 1,-1, 1, 0): 'finishes',
    ( 1,-1, 1, 1): 'overlapped-by',( 1, 0, 1, 1): 'met-by',
    ( 1, 1, 1, 1): 'after',
}
CARDINAL_NAMES = {
    ('before', 'before'):  'south-west',
    ('before', 'overlap'): 'west',
    ('before', 'after'):   'north-west',
    ('overlap','before'):  'south',
    ('overlap','overlap'): 'overlapping',
    ('overlap','after'):   'north',
    ('after',  'before'):  'south-east',
    ('after',  'overlap'): 'east',
    ('after',  'after'):   'north-east',
}

RCC8_NAMES = {
    'DC':    'disconnected-from',
    'EC':    'touches',
    'PO':    'partially-overlaps',
    'EQ':    'equals',
    'TPP':   'tangential-part-of',
    'NTPP':  'non-tangential-part-of',
    'TPPi':  'has-tangential-part',
    'NTPPi': 'has-non-tangential-part',
}

_id = lambda r: r

# ---- Build calculi (all under a second of module load) -----------------

ALLEN_CALC    = derive('allen',  all_intervals, allen,     N=4)
RCC8_CALC     = derive('rcc8',   all_intervals, rcc8_iv,   N=3)
COARSE_CALC   = derive('coarse', all_intervals, coarse_iv, N=3)
CARDINAL_CALC = derive_product('cardinal', COARSE_CALC)

assert len(ALLEN_CALC.base)    == 13
assert len(RCC8_CALC.base)     == 8
assert len(COARSE_CALC.base)   == 3
assert len(CARDINAL_CALC.base) == 9

# ---- Registry: shared calculi, calculus-specific runtime semantics -----

_INT_POOL = all_intervals(4)
_BOX_POOL = all_boxes(3)

REGISTRY = {
    'allen_time': dict(calc=ALLEN_CALC, pool=_INT_POOL, rel=allen,
                       label=ALLEN_NAMES.__getitem__,
                       topic='time intervals',
                       phrasing='the temporal relation of interval {i} to interval {j}'),
    'allen_x':    dict(calc=ALLEN_CALC, pool=_BOX_POOL, rel=hdir,
                       label=ALLEN_NAMES.__getitem__,
                       topic='horizontal extents of 2D boxes',
                       phrasing='the relation of the horizontal extent of box {i} to that of box {j}'),
    'allen_y':    dict(calc=ALLEN_CALC, pool=_BOX_POOL, rel=vdir,
                       label=ALLEN_NAMES.__getitem__,
                       topic='vertical extents of 2D boxes',
                       phrasing='the relation of the vertical extent of box {i} to that of box {j}'),
    'rcc8': dict(calc=RCC8_CALC, pool=_BOX_POOL, rel=rcc8_box,
                 label=RCC8_NAMES.__getitem__,
                 topic='2D regions (axis-aligned boxes)',
                 phrasing='the spatial relation of region {i} to region {j}'),
    'cardinal':   dict(calc=CARDINAL_CALC, pool=_BOX_POOL, rel=cardinal_box,
                       label=CARDINAL_NAMES.__getitem__,
                       topic='2D boxes by cardinal direction',
                       phrasing='the cardinal direction of box {i} relative to box {j}'),
}

# ---- Tree utilities -----------------------------------------------------

def random_tree(n):
    nodes = list(range(n)); random.shuffle(nodes)
    return [(nodes[i], random.choice(nodes[:i])) for i in range(1, n)]

def farthest_pair(n, edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    def bfs(src):
        dist = {src: 0}; q = deque([src]); far = src
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    if dist[v] > dist[far]: far = v
                    q.append(v)
        return far, dist[far]
    a, _ = bfs(0)
    b, d = bfs(a)
    return a, b, d

# ---- Ordinal ranking ----------------------------------------------------

def _ordinal_label(k):
    if 10 <= k % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(k % 10, "th")
    return f"{k}{suffix}"

def _rank_label(k, direction):
    if k == 1:
        return direction
    return f"{_ordinal_label(k)}-{direction}"

def _rank_expr(pos, clue):
    a = clue["a"]
    if clue["kind"] == "rank":
        return pos[a] == clue["rank"]
    b = clue["b"]
    return pos[a] + 1 == pos[b] if clue["kind"] == "next" else pos[a] < pos[b]

def _rank_text(clue):
    a = clue["a"]
    if clue["kind"] == "rank":
        k = clue["rank"] + 1
        return f"{a} is the {_rank_label(k, 'newest')}."
    b = clue["b"]
    word = "immediately newer" if clue["kind"] == "next" else "newer"
    return f"{a} is {word} than {b}."

def _rank_candidates(n, clues, query_rank):
    pos = {f"E{i}": Int(f"rank_E{i}") for i in range(n)}
    solver = Solver()
    solver.add(Distinct(*pos.values()))
    solver.add(*[p >= 0 for p in pos.values()], *[p < n for p in pos.values()])
    solver.add(*[_rank_expr(pos, clue) for clue in clues])
    return [
        name for name, p in pos.items()
        if solver.check(p == query_rank) == sat
    ]

def _rank_redundant(clue, clues):
    return clue["kind"] in {"pair", "next"} and any(
        {clue["kind"], other["kind"]} == {"pair", "next"}
        and clue["a"] == other["a"] and clue["b"] == other["b"]
        for other in clues
    )

# ---- Task ---------------------------------------------------------------

@dataclass
class QualitativeReasoningConfig(Config):
    n_entities: int = 5
    extra_edges: int = 0
    ordinal_prob: float = 0.35

    def apply_difficulty(self, level):
        self.n_entities = sround(self.n_entities + level)
        self.extra_edges = sround(self.extra_edges + 0.5 * level)

class QualitativeReasoning(Task):
    summary = "Solve qualitative spatial and temporal reasoning problems over algebras."
    def __init__(self, config=None):
        super().__init__(config=config or QualitativeReasoningConfig())

    def generate(self):
        if random.random() < self.config.ordinal_prob:
            return self._ordinal_problem()
        for _ in range(80):
            p = self._try()
            if p is not None:
                return p
        raise RuntimeError("QualitativeReasoning: could not build instance")

    def _ordinal_problem(self):
        if self.config.n_entities < 4:
            min_clues = 2
        else:
            min_clues = random.choices([2, 3, 4], weights=[1, 2, 7])[0]
        for _ in range(80):
            problem = self._try_ordinal_problem(min_clues)
            if problem is not None:
                return problem
        raise RuntimeError("Could not build a non-trivial ordinal ranking problem")

    def _try_ordinal_problem(self, min_clues):
        n = max(3, int(self.config.n_entities))
        entities = [f"E{i}" for i in range(n)]
        order = random.sample(entities, n)  # newest to oldest
        query_rank = random.randrange(1, n - 1) if n >= 4 else 1

        pools = {
            "pair": [
                {"kind": "pair", "a": order[i], "b": order[j]}
                for i in range(n) for j in range(i + 1, n)
            ],
            "next": [
                {"kind": "next", "a": order[i], "b": order[i + 1]}
                for i in range(n - 1)
            ],
            "rank": [
                {"kind": "rank", "a": order[i], "rank": i}
                for i in range(n) if i != query_rank
            ],
        }
        required = random.sample(list(pools), 2)
        clues = []
        for kind in required:
            random.shuffle(pools[kind])
            choices = [c for c in pools[kind] if not _rank_redundant(c, clues)]
            clue = min(
                choices,
                key=lambda c: len(_rank_candidates(n, clues + [c], query_rank)),
            )
            clues.append(clue)
            pools[kind].remove(clue)

        pool = sum(pools.values(), [])
        random.shuffle(pool)
        while len(_rank_candidates(n, clues, query_rank)) != 1 and pool:
            pool = [c for c in pool if not _rank_redundant(c, clues)]
            if not pool:
                break
            current = len(_rank_candidates(n, clues, query_rank))
            improving = [
                c for c in pool
                if len(_rank_candidates(n, clues + [c], query_rank)) < current
            ]
            clue = random.choice(improving or pool)
            clues.append(clue)
            pool.remove(clue)

        for clue in clues[::-1]:
            reduced = [c for c in clues if c is not clue]
            if len({c["kind"] for c in reduced}) >= 2 and len(_rank_candidates(n, reduced, query_rank)) == 1:
                clues = reduced

        candidates = _rank_candidates(n, clues, query_rank)
        min_clues = min(min_clues, n - 1)
        if len(candidates) != 1 or len(clues) < min_clues:
            return None
        random.shuffle(clues)

        from_oldest = random.random() < 0.5
        k = n - query_rank if from_oldest else query_rank + 1
        return Problem(
            metadata=edict(
                family="ordinal", n_entities=n, entities=entities,
                clues=clues, clue_text=[_rank_text(c) for c in clues],
                query_rank=query_rank, query_direction="oldest" if from_oldest else "newest",
                query_k=k, hidden_order=order,
                intro=(
                    f"There are {n} objects: {', '.join(entities)}.\n"
                    "They have distinct ages."
                ),
                facts=[_rank_text(c) for c in clues],
                question=f"Which object is the {_rank_label(k, 'oldest' if from_oldest else 'newest')}?",
                answer_instruction="The answer is one object label.",
            ),
            answer=candidates[0],
        )

    def _try(self):
        cfg = self.config
        key = random.choice(list(REGISTRY))
        spec = REGISTRY[key]
        calc, pool, rel = spec['calc'], spec['pool'], spec['rel']
        label, topic, phrasing = spec['label'], spec['topic'], spec['phrasing']
        n = max(3, int(cfg.n_entities))

        ents = [random.choice(pool) for _ in range(n)]
        gt = {(i, j): rel(ents[i], ents[j])
              for i in range(n) for j in range(n) if i != j}

        tree = random_tree(n)
        qi, qj, hops = farthest_pair(n, tree)
        if hops < 2:
            return None

        all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        tree_set  = {frozenset(e) for e in tree}
        query_set = frozenset({qi, qj})
        extras_pool = [e for e in all_pairs
                       if frozenset(e) not in tree_set
                       and frozenset(e) != query_set]
        random.shuffle(extras_pool)

        n_extra = max(0, int(cfg.extra_edges))
        revealed = list(tree) + extras_pool[:n_extra]
        leftover = extras_pool[n_extra:]

        hard = {e: frozenset({gt[e]}) for e in revealed}
        R = closure(calc, n, hard)
        while R is not None and len(R[qi, qj]) > 1 and leftover:
            e = leftover.pop()
            hard[e] = frozenset({gt[e]})
            revealed.append(e)
            R = closure(calc, n, hard)

        if R is None or len(R[qi, qj]) != 1:
            return None
        truth = next(iter(R[qi, qj]))
        if truth != gt[qi, qj]:
            return None  # impossible if PC is sound; defensive

        vocab = sorted({label(r) for r in calc.base})
        metadata = edict(
            calculus=key, topic=topic, phrasing=phrasing,
            n_entities=n, hops=hops, n_revealed=len(revealed),
            entities=ents,
            revealed=[(i, j, label(gt[i, j])) for (i, j) in revealed],
            query=(qi, qj), vocabulary=vocab,
            intro=(
                f"There are {n} entities labeled 0 through {n - 1}.\n"
                "Read 'i rel j' as 'entity i is rel to entity j'."
            ),
            facts=[f"{i} {label(gt[i, j])} {j}" for i, j in revealed],
            question=f"What is {phrasing.format(i=qi, j=qj)}?",
            answer_instruction=f"The answer is exactly one of: {', '.join(vocab)}.",
        )
        return Problem(metadata=metadata, answer=label(gt[qi, qj]))

    def prompt(self, metadata):
        facts = "\n".join(f"- {x}" for x in metadata.facts)
        return (
            f"{metadata.intro}\n"
            f"Facts:\n{facts}\n\n"
            f"{metadata.question}\n"
            f"{metadata.answer_instruction}"
        )
        
    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        norm = lambda s: str(s).strip().lower().replace('_', '-')
        return float(norm(answer) == norm(entry.answer))
