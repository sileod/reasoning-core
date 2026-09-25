import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'ribbon_surface_surgery (variant 1 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/ribbon_surface_surgery',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2305351643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class RibbonSurfaceSurgeryConfig(Config):
    n_vertices: int = 3
    n_operations: int = 3

    def apply_difficulty(self, level):
        self.n_vertices = stochastic_rounding(self.n_vertices + level)
        self.n_operations = stochastic_rounding(self.n_operations + level)


class RibbonSurfaceSurgery(Task):
    summary = ("Track oriented ribbon surfaces through edge deletion, contraction, "
               "band attachment, and vertex splitting using cyclic half-edge orders; "
               "return the resulting boundary components and genus.")
    design_choice = ("Represent the ribbon surface via a cyclic half-edge permutation per "
                     "vertex, and output the boundary as a list of half-edge labels in "
                     "traversal order, with genus as a separate integer.")
    config_cls = RibbonSurfaceSurgeryConfig
    task_version = 2

    def generate_entry(self):
        n_vertices = int(self.config.n_vertices)
        n_ops = int(self.config.n_operations)
        for _ in range(30):
            built = _build_surface(n_vertices, n_ops)
            if built is None:
                continue
            sigma, alpha, initial, ops, boundary, genus = built
            return Entry(
                metadata={
                    "initial_cycles": {str(k): v for k, v in initial["cycles"].items()},
                    "initial_pairs": [list(p) for p in initial["pairs"]],
                    "ops": ops,
                    "boundary": boundary,
                    "genus": int(genus),
                },
                answer=_format_answer(boundary, genus),
            )
        raise RuntimeError("ribbon_surface_surgery: could not build a valid instance")

    def render_prompt(self, metadata):
        return _render_prompt(metadata)

    def score_answer(self, answer, entry):
        gold = _format_answer(entry.metadata["boundary"], entry.metadata["genus"])
        if isinstance(answer, str) and answer.strip() == gold:
            return 1.0
        return 0.0


def _format_answer(boundary, genus):
    return "B=[" + ",".join(str(x) for x in boundary) + "];g=" + str(genus)


def _render_prompt(metadata):
    lines = []
    lines.append(
        "We model an oriented ribbon surface (fat graph / band decomposition) by its "
        "half-edges. Every half-edge has an integer label. Each edge glues two "
        "half-edges together as a mate-pair. At each vertex the half-edges are arranged "
        "in a counter-clockwise cyclic order; the rotation cycle of a vertex lists them "
        "in that order."
    )
    lines.append(
        "The boundary of the surface is read by walking: from a half-edge d, move to "
        "its successor s in d's rotation cycle, then jump across the edge to s's mate, "
        "then repeat. Each closed walk so obtained is one boundary component, and the "
        "half-edge labels in traversal order form that component's list."
    )
    lines.append(
        "The genus is the usual oriented-surface genus of the resulting ribbon surface, "
        "determined by its final rotation cycles and mate-pairs through Euler's formula."
    )
    lines.append(
        "Operations (each rule stated once, applied in the listed order): "
        "band_attach(a,b) makes a new edge whose two new half-edges n1 and n2 are "
        "inserted immediately after half-edge a and immediately after half-edge b in "
        "their rotation cycles, and n1,n2 are mates of each other. "
        "del(x) deletes the edge whose one side is half-edge x (x and its mate are "
        "removed) and splices the two affected rotation cycles so each removed "
        "half-edge's counter-clockwise predecessor now points to its successor. "
        "con(x) contracts the edge with sides x and x'=mate(x), at distinct vertices "
        "U and W; with a=successor(x) in U and b=successor(x') in W, the two vertices "
        "merge into one whose rotation joins the two cycles so that b follows the "
        "counter-clockwise predecessor of x and a follows that of x'. "
        "split_vertex(c,k) cuts vertex V, whose rotation is linearized starting from "
        "its smallest half-edge label, at the k-th smallest label c; new half-edge n1 "
        "opens the vertex that receives the counter-clockwise segment starting at c "
        "(back to just before c), new half-edge n2 opens the vertex that receives the "
        "remaining earlier segment, and n1,n2 are mates of the new edge."
    )

    lines.append("Initial rotation cycles (vertex id = smallest half-edge label):")
    for v in sorted(metadata["initial_cycles"], key=int):
        cyc = metadata["initial_cycles"][v]
        lines.append(f"  vertex {v}: " + ",".join(str(d) for d in cyc) + " (cycle)")
    lines.append("Initial mate-pairs of edges: " + _fmt_initial_pairs(metadata["initial_pairs"]))

    lines.append("Operations applied in order:")
    for i, op in enumerate(metadata["ops"], 1):
        lines.append(f"  {i}. " + _fmt_op(op))

    lines.append(
        "Give the final boundary components as a list of half-edge labels in traversal "
        "order (start each component at its smallest label; order the components by "
        "increasing smallest label), and the genus, as a single line in the format: "
        "B=[label1,label2,...];g=GENUS"
    )
    return "\n".join(lines)


def _fmt_initial_pairs(pairs):
    if pairs:
        return "(" + ",".join(f"{a}-{b}" for a, b in pairs) + ")"
    return "(none)"


def _fmt_op(op):
    t = op["type"]
    if t == "band":
        return (f"band_attach({op['a']},{op['b']}): new edge with new half-edges "
                f"{op['new1']} after {op['a']} and {op['new2']} after {op['b']}")
    if t == "del":
        return f"del({op['x']}): delete the edge whose one side is half-edge {op['x']} "
    if t == "con":
        return (f"con({op['x']}): contract the edge with sides {op['x']} and "
                f"{op['mate']}")
    if t == "split":
        return (f"split_vertex({op['c']}, k={op['k']}): split the vertex containing "
                f"half-edge {op['c']}; new half-edges {op['n1']} and {op['n2']} open "
                f"the two segments")
    return str(op)


def _rotation_cycles(sigma):
    seen = set()
    cycles = []
    for d in sorted(sigma):
        if d in seen:
            continue
        cyc = []
        cur = d
        guard = 0
        while cur in sigma and cur not in seen and guard < len(sigma) + 2:
            seen.add(cur)
            cyc.append(cur)
            nxt = sigma.get(cur)
            if nxt is None or nxt not in sigma:
                break
            cur = nxt
            guard += 1
        cycles.append(cyc)
    return cycles


def _boundary_components(sigma, alpha):
    seen = set()
    comps = []
    for d in sorted(sigma):
        if d in seen:
            continue
        orbit = []
        cur = d
        while cur in sigma and cur not in seen:
            seen.add(cur)
            orbit.append(cur)
            nxt = sigma.get(cur)
            if nxt is None or nxt not in alpha:
                break
            cur = alpha[nxt]
        comps.append(orbit)
    return comps


def _closure_ok(sigma, alpha):
    if set(sigma) != set(alpha):
        return False
    for d in sigma:
        m = alpha.get(d)
        if m is None or m == d or alpha.get(m) != d:
            return False
    return True


def _invariant(sigma, alpha):
    if set(sigma.values()) != set(sigma.keys()):
        return None
    cycles = _rotation_cycles(sigma)
    if any(len(c) == 0 for c in cycles):
        return None
    if not _closure_ok(sigma, alpha):
        return None
    V = len(cycles)
    seen = set()
    E = 0
    for d in sorted(alpha):
        if d not in seen:
            seen.add(d)
            seen.add(alpha[d])
            E += 1
    b = len(_boundary_components(sigma, alpha))
    vids = {min(c) for c in cycles}
    parent = {v: v for v in vids}
    d2v = {d: min(c) for c in cycles for d in c}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for d in sorted(alpha):
        dd = alpha[d]
        if d in d2v and dd in d2v:
            union(d2v[d], d2v[dd])
    roots = {find(x) for x in vids}
    if len(roots) != 1:
        return None
    numerator = 2 - V + E - b
    if numerator < 0 or numerator % 2 != 0:
        return None
    g = numerator // 2
    if g < 0 or g > 60:
        return None
    return (V, E, b, g)


def _build_surface(n_vertices, n_ops):
    sigma = {0: 1, 1: 0}
    alpha = {0: 1, 1: 0}
    next_dart = 2

    target = max(1, int(n_vertices))
    safety = 0
    while len(_rotation_cycles(sigma)) < target and safety < 80:
        safety += 1
        res = _split_random(sigma, alpha, next_dart)
        if res is None:
            res = _band_random(sigma, alpha, next_dart)
            if res is None:
                break
        sigma = res[0]
        alpha = res[1]
        next_dart = res[2]

    init_cycles_raw = _rotation_cycles(sigma)
    initial_cycles = {}
    for c in init_cycles_raw:
        m = min(c)
        idx = c.index(m)
        initial_cycles[m] = c[idx:] + c[:idx]
    initial = {"cycles": initial_cycles, "pairs": _current_pairs(alpha)}

    ops = []
    for _ in range(int(n_ops)):
        placed = False
        for _ in range(10):
            choice = random.random()
            if choice < 0.30:
                cand = _band_random(sigma, alpha, next_dart)
            elif choice < 0.52:
                cand = _del_random(sigma, alpha, next_dart)
            elif choice < 0.76:
                cand = _con_random(sigma, alpha, next_dart)
            else:
                cand = _split_random(sigma, alpha, next_dart)
            if cand is not None:
                sigma, alpha, next_dart, opdesc = cand
                ops.append(opdesc)
                placed = True
                break
        if not placed:
            # even a self-loop band always works on a connected surface
            cand = _band_random(sigma, alpha, next_dart)
            if cand is None:
                return None
            sigma, alpha, next_dart, opdesc = cand
            ops.append(opdesc)

    inv = _invariant(sigma, alpha)
    if inv is None:
        return None
    _, _, _, genus = inv
    bd = _canonical_boundary(_boundary_components(sigma, alpha))
    if not bd:
        return None
    return sigma, alpha, initial, ops, bd, genus


def _current_pairs(alpha):
    seen = set()
    pairs = []
    for d in sorted(alpha):
        if d not in seen:
            seen.add(d)
            seen.add(alpha[d])
            pairs.append((d, alpha[d]))
    pairs.sort()
    return pairs


def _canonical_boundary(comps):
    result = []
    for c in comps:
        if not c:
            continue
        m = min(c)
        idx = c.index(m)
        result.append(tuple(c[idx:] + c[:idx]))
    result.sort(key=lambda t: t[0])
    return [x for t in result for x in t]


def _band_random(sigma, alpha, next_dart):
    darts = sorted(sigma)
    a = random.choice(darts)
    b = random.choice(darts)
    return _band(sigma, alpha, next_dart, a, b)


def _band(sigma, alpha, next_dart, a, b):
    n1, n2 = next_dart, next_dart + 1
    s = dict(sigma)
    al = dict(alpha)
    sa = s[a]
    sb = s[b]
    s[a] = n1
    s[n1] = sa
    s[b] = n2
    s[n2] = sb
    al[n1] = n2
    al[n2] = n1
    if _invariant(s, al) is None:
        return None
    return s, al, next_dart + 2, {"type": "band", "a": a, "b": b,
                                  "new1": n1, "new2": n2}


def _del_random(sigma, alpha, next_dart):
    candidates = []
    for d in sorted(alpha):
        if alpha[d] > d:
            candidates.append(d)
    random.shuffle(candidates)
    for d in candidates:
        res = _del(sigma, alpha, next_dart, d)
        if res is not None:
            return res
    return None


def _del(sigma, alpha, next_dart, x):
    xm = alpha[x]
    s = dict(sigma)
    al = dict(alpha)
    px = _pred(s, x)
    sx = s.get(x)
    pxm = _pred(s, xm)
    sxm = s.get(xm)
    if sx is None or sxm is None:
        return None
    if s.get(px) == x:
        s[px] = sx
    if s.get(pxm) == xm:
        s[pxm] = sxm
    s.pop(x, None)
    s.pop(xm, None)
    al.pop(x, None)
    al.pop(xm, None)
    if _invariant(s, al) is None:
        return None
    return s, al, next_dart, {"type": "del", "x": x, "mate": xm}


def _pred(s, d):
    if d not in s:
        return None
    for cand in s:
        if s[cand] == d:
            return cand
    return None


def _con_random(sigma, alpha, next_dart):
    candidates = []
    for d in sorted(alpha):
        if alpha[d] > d:
            if _vertex_of(d, sigma) != _vertex_of(alpha[d], sigma):
                candidates.append(d)
    random.shuffle(candidates)
    for d in candidates:
        res = _con(sigma, alpha, next_dart, d)
        if res is not None:
            return res
    return None


def _vertex_of(d, sigma):
    seen = set()
    cur = d
    while cur not in seen:
        seen.add(cur)
        cur = sigma[cur]
    return min(seen)


def _con(sigma, alpha, next_dart, x):
    xm = alpha[x]
    s = dict(sigma)
    al = dict(alpha)
    if x not in s or xm not in s:
        return None
    px = _pred(s, x)
    ax = s[x]
    pxm = _pred(s, xm)
    bxm = s[xm]
    if ax is None or bxm is None or px is None or pxm is None:
        return None
    s.pop(x, None)
    s.pop(xm, None)
    al.pop(x, None)
    al.pop(xm, None)
    s[px] = bxm
    s[pxm] = ax
    if _invariant(s, al) is None:
        return None
    return s, al, next_dart, {"type": "con", "x": x, "mate": xm}


def _split_random(sigma, alpha, next_dart):
    cycles = _rotation_cycles(sigma)
    random.shuffle(cycles)
    for cyc in cycles:
        if len(cyc) < 2:
            continue
        m = min(cyc)
        idx = cyc.index(m)
        lin = cyc[idx:] + cyc[:idx]
        k = random.randint(1, len(lin) - 1)
        res = _split(sigma, alpha, next_dart, lin[k], k, lin)
        if res is not None:
            return res
    return None


def _split(sigma, alpha, next_dart, c, k, lin):
    n1, n2 = next_dart, next_dart + 1
    s = dict(sigma)
    al = dict(alpha)
    pos = lin.index(c)
    early = lin[:pos]
    late = lin[pos:]
    s1 = [n1] + late
    s2 = [n2] + early
    al[n1] = n2
    al[n2] = n1
    for d in lin:
        s.pop(d, None)
    for i in range(len(s1)):
        s[s1[i]] = s1[(i + 1) % len(s1)]
    for i in range(len(s2)):
        s[s2[i]] = s2[(i + 1) % len(s2)]
    if _invariant(s, al) is None:
        return None
    return s, al, next_dart + 2, {"type": "split", "c": c, "k": pos,
                                  "n1": n1, "n2": n2}


def _replay(metadata):
    cycles = {int(k): list(v) for k, v in metadata["initial_cycles"].items()}
    sigma = {}
    for cyc in cycles.values():
        for i in range(len(cyc)):
            sigma[cyc[i]] = cyc[(i + 1) % len(cyc)]
    alpha = {}
    for a, b in metadata["initial_pairs"]:
        alpha[int(a)] = int(b)
        alpha[int(b)] = int(a)
    used = set()
    for v in cycles.values():
        for d in v:
            used.add(d)
    for a, b in metadata["initial_pairs"]:
        used.add(int(a))
        used.add(int(b))
    next_dart = (max(used) + 1) if used else 2
    for op in metadata["ops"]:
        t = op["type"]
        if t == "band":
            res = _band(sigma, alpha, next_dart, op["a"], op["b"])
            assert res is not None
            sigma, alpha, next_dart, _ = res
        elif t == "del":
            res = _del(sigma, alpha, next_dart, op["x"])
            assert res is not None
            sigma, alpha, next_dart, _ = res
        elif t == "con":
            res = _con(sigma, alpha, next_dart, op["x"])
            assert res is not None
            sigma, alpha, next_dart, _ = res
        elif t == "split":
            lin = None
            for c in _rotation_cycles(sigma):
                if op["c"] in c:
                    m = min(c)
                    idx = c.index(m)
                    lin = c[idx:] + c[:idx]
                    break
            assert lin is not None
            res = _split(sigma, alpha, next_dart, op["c"], op["k"], lin)
            assert res is not None
            sigma, alpha, next_dart, _ = res
    return sigma, alpha
