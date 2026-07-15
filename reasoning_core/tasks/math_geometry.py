import random
import re
from copy import copy
from dataclasses import dataclass, field

import sympy as sp
from sympy.geometry import Point, Line, Segment

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround


LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ID_RE = re.compile(r"p\d+")
NUM_RE = r"[+-]?\d+(?:/\d+)?"


def q(x):
    x = sp.Rational(x)
    return str(int(x)) if x.q == 1 else f"{x.p}/{x.q}"


def pstr(P):
    return f"({q(P.x)}, {q(P.y)})"


def key(P):
    return sp.Rational(P.x), sp.Rational(P.y)


def parse_point(s):
    m = re.fullmatch(rf"\s*\(?\s*({NUM_RE})\s*,\s*({NUM_RE})\s*\)?\s*\.?\s*", str(s))
    return None if not m else Point(sp.Rational(m.group(1)), sp.Rational(m.group(2)))


def clean(s):
    return re.sub(r"[\s`]+", " ", str(s).strip()).strip(" .").lower()


def clean_labels(s):
    return re.sub(r"[\s`]+", "", str(s).upper()).strip(".,;")


def cross(A, B, C):
    return (B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x)


def dot(A, B, C):
    return (A.x - B.x) * (C.x - B.x) + (A.y - B.y) * (C.y - B.y)


def dsq(A, B):
    return (A.x - B.x) ** 2 + (A.y - B.y) ** 2


def line_intersection(A, B, C, D):
    if A == B or C == D:
        return None
    xs = Line(A, B).intersection(Line(C, D))
    return xs[0] if len(xs) == 1 and isinstance(xs[0], Point) else None


def orientation(A, B, P):
    z = cross(A, B, P)
    return "left" if z > 0 else "right" if z < 0 else "on"


def on_segment(A, B, P):
    return (
        cross(A, B, P) == 0
        and min(A.x, B.x) <= P.x <= max(A.x, B.x)
        and min(A.y, B.y) <= P.y <= max(A.y, B.y)
    )


def line_relation(A, B, C, D):
    ux, uy = B.x - A.x, B.y - A.y
    vx, vy = D.x - C.x, D.y - C.y
    z = ux * vy - uy * vx
    d = ux * vx + uy * vy
    return "parallel" if z == 0 else "perpendicular" if d == 0 else "neither"


def angle_type(A, B, C):
    if cross(A, B, C) == 0:
        return None
    d = dot(A, B, C)
    return "acute" if d > 0 else "right" if d == 0 else "obtuse"


def triangle_position(A, B, C, P):
    if any(on_segment(U, V, P) for U, V in ((A, B), (B, C), (C, A))):
        return "boundary"
    s = [cross(A, B, P), cross(B, C, P), cross(C, A, P)]
    return "inside" if all(x > 0 for x in s) or all(x < 0 for x in s) else "outside"


def small_point(P, cfg):
    return all(sp.Rational(v).q <= cfg.max_den and abs(sp.Rational(v).p) <= cfg.max_num for v in P.args)


def rand_point(m):
    return Point(random.randint(-m, m), random.randint(-m, m))


def rand_nonzero(a, b):
    x = 0
    while x == 0:
        x = random.randint(a, b)
    return x


def rand_frac(den, proper=True):
    d = random.randint(2, den)
    if proper:
        return sp.Rational(random.randint(1, d - 1), d)
    n = random.randint(-2 * d, 3 * d)
    return sp.Rational(n + (n in (0, d)), d)


def rand_vector(m):
    while True:
        P = Point(random.randint(-m, m), random.randint(-m, m))
        if P != Point(0, 0):
            return P


def frac_scale(cfg):
    return rand_frac(cfg.max_interp_den, proper=True)


def scale_points(points, cfg):
    s = frac_scale(cfg)
    return [Point(s * P.x, s * P.y) for P in points]


def affine_points(coords, cfg):
    """Map canonical rational coordinates through a random nonsingular basis."""
    for _ in range(cfg.max_tries):
        u, v = rand_vector(cfg.coord_abs), rand_vector(cfg.coord_abs)
        if u.x * v.y == u.y * v.x:
            continue
        s = frac_scale(cfg)
        return [Point(s * (x * u.x + y * v.x), s * (x * u.y + y * v.y)) for x, y in coords]
    return None


def local_ids(scene, rel_points, cfg):
    """Use one class-independent scene anchor and add every other local point."""
    anchor = sample_ids(scene, 1, cfg)
    if not anchor or not rel_points:
        return None, []
    anchor = anchor[0]
    j = random.randrange(len(rel_points))
    O, R = scene["points"][anchor], rel_points[j]
    points = [Point(O.x + P.x - R.x, O.y + P.y - R.y) for P in rel_points]
    if len({key(P) for P in points}) != len(points):
        return None, []

    additions, ids = [], []
    for i, P in enumerate(points):
        if i == j:
            ids.append(anchor)
            continue
        p = candidate(scene, additions, P, cfg)
        if p is None:
            return None, []
        ids.append(p)
    return ids, additions


def query_result(type_, kind, answer, additions, question, instruction, balance, subtype=None):
    return edict(
        type=type_, kind=kind, answer=answer, additions=additions,
        question=question, instruction=instruction,
        balance=f"{balance}:{subtype}" if subtype else balance,
        construction_family=subtype,
    )


def add_point(scene, P, definition=None, depth=0):
    i = f"p{len(scene['points'])}"
    scene["points"][i] = P
    scene["depth"][i] = depth
    if definition:
        scene["definitions"][i] = definition
    return i


def exists(scene, additions, P):
    return key(P) in {key(x) for x in scene["points"].values()} | {key(x[1]) for x in additions}


def candidate(scene, additions, P, cfg, definition=None, depth=0):
    if not small_point(P, cfg) or exists(scene, additions, P):
        return None
    i = f"p{len(scene['points']) + len(additions)}"
    additions.append((i, P, definition, depth))
    return i


def sample_ids(scene, k, cfg, constructed=None):
    ids = list(scene["points"])
    if len(ids) < k:
        return None

    constructed = (
        any(scene["depth"][i] > 0 for i in ids) and random.random() < cfg.constructed_operand_prob
        if constructed is None else constructed
    )

    for _ in range(cfg.max_tries):
        out = []
        while len(out) < k:
            pool = [i for i in ids if i not in out]
            weights = [1 + cfg.constructed_operand_weight * scene["depth"][i] for i in pool]
            out.append(random.choices(pool, weights=weights)[0])
        if not constructed or any(scene["depth"][i] > 0 for i in out):
            return out
    return None


def render_text(s, labels):
    return ID_RE.sub(lambda m: labels[m.group(0)], s)


def render(scene, query, construction_execution=False):
    points = dict(scene["points"])
    definitions = dict(scene["definitions"])

    for i, P, definition, _ in query.additions:
        points[i] = P
        if definition:
            definitions[i] = definition

    ids = list(points)
    labels = dict(zip(ids, random.sample(LABELS, len(ids))))

    shown_ids = [i for i in ids if not construction_execution or i not in definitions]
    shown = edict({labels[i]: pstr(points[i]) for i in sorted(shown_ids, key=lambda x: labels[x])})
    defs = (
        [f"{labels[i]} is {render_text(definitions[i], labels)}." for i in definitions]
        if construction_execution else []
    )

    if query.kind in {"label", "label_or_tie"}:
        answer = query.answer if query.answer == "tie" else labels[query.answer]
    elif query.kind == "labels":
        answer = ",".join(labels[i] for i in query.answer)
    else:
        answer = query.answer

    return edict(
        points=shown,
        definitions=defs,
        query=render_text(query.question, labels),
        instruction=render_text(query.instruction, labels),
        query_type=query.type,
        answer_kind=query.kind,
        balance=query.balance,
        construction_family=getattr(query, "construction_family", None),
        answer=answer,
        internal_query=query.question,
    )


def construct_midpoint(scene, cfg):
    ids = sample_ids(scene, 2, cfg, constructed=False)
    if not ids:
        return False
    a, b = ids
    A, B = scene["points"][a], scene["points"][b]
    if A == B:
        return False
    P = Segment(A, B).midpoint
    if not small_point(P, cfg) or key(P) in {key(Q) for Q in scene["points"].values()}:
        return False
    add_point(scene, P, f"the midpoint of {a} and {b}", max(scene["depth"][a], scene["depth"][b]) + 1)
    return True


def construct_intersection(scene, cfg):
    ids = sample_ids(scene, 4, cfg)
    if not ids:
        return False
    a, b, c, d = ids
    P = line_intersection(*(scene["points"][i] for i in ids))
    if P is None or not small_point(P, cfg) or key(P) in {key(Q) for Q in scene["points"].values()}:
        return False
    add_point(scene, P, f"the intersection of lines {a}{b} and {c}{d}", max(scene["depth"][i] for i in ids) + 1)
    return True


def construct_projection(scene, cfg):
    ids = sample_ids(scene, 3, cfg)
    if not ids:
        return False
    p, a, b = ids
    A, B, P0 = scene["points"][a], scene["points"][b], scene["points"][p]
    if A == B:
        return False
    P = Line(A, B).projection(P0)
    if not small_point(P, cfg) or key(P) in {key(Q) for Q in scene["points"].values()}:
        return False
    add_point(scene, P, f"the projection of {p} onto line {a}{b}", max(scene["depth"][i] for i in ids) + 1)
    return True


def construct_reflection(scene, cfg):
    ids = sample_ids(scene, 3, cfg)
    if not ids:
        return False
    p, a, b = ids
    A, B, P0 = scene["points"][a], scene["points"][b], scene["points"][p]
    if A == B:
        return False
    P = P0.reflect(Line(A, B))
    if not small_point(P, cfg) or key(P) in {key(Q) for Q in scene["points"].values()}:
        return False
    add_point(scene, P, f"the reflection of {p} across line {a}{b}", max(scene["depth"][i] for i in ids) + 1)
    return True


def construct_translate(scene, cfg):
    ids = sample_ids(scene, 3, cfg)
    if not ids:
        return False
    p, a, b = ids
    P0, A, B = (scene["points"][i] for i in ids)
    P = Point(P0.x + B.x - A.x, P0.y + B.y - A.y)
    if not small_point(P, cfg) or key(P) in {key(Q) for Q in scene["points"].values()}:
        return False
    add_point(scene, P, f"the translation of {p} by vector {a}{b}", max(scene["depth"][i] for i in ids) + 1)
    return True


def construct_rot90(scene, cfg):
    ids = sample_ids(scene, 2, cfg)
    if not ids:
        return False
    p, o = ids
    P0, O = scene["points"][p], scene["points"][o]
    P = Point(O.x - (P0.y - O.y), O.y + (P0.x - O.x))
    if not small_point(P, cfg) or key(P) in {key(Q) for Q in scene["points"].values()}:
        return False
    add_point(scene, P, f"the 90-degree counterclockwise rotation of {p} about {o}", max(scene["depth"][i] for i in ids) + 1)
    return True


CONSTRUCTORS = [
    construct_midpoint,
    construct_intersection,
    construct_projection,
    construct_reflection,
    construct_translate,
    construct_rot90,
]


def make_scene(cfg):
    scene = {"points": {}, "definitions": {}, "depth": {}}
    seen = set()

    while len(scene["points"]) < max(4, min(cfg.n_base_points, 18)):
        P = rand_point(max(2, cfg.coord_abs))
        if key(P) not in seen:
            add_point(scene, P, depth=0)
            seen.add(key(P))

    target = min(cfg.n_constructed_points, len(LABELS) - len(scene["points"]) - 6)
    for _ in range(max(0, target)):
        for _ in range(cfg.max_tries):
            if random.choice(CONSTRUCTORS)(scene, cfg):
                break

    return scene


def query_orientation(scene, cfg):
    want = random.choice(["left", "right", "on"])
    for _ in range(cfg.max_tries):
        u, t = rand_vector(cfg.coord_abs), rand_frac(cfg.max_interp_den, False)
        h = 1
        side = 0 if want == "on" else h if want == "left" else -h
        rel = scale_points([Point(0, 0), u, Point(t*u.x-side*u.y, t*u.y+side*u.x)], cfg)
        ids, additions = local_ids(scene, rel, cfg)
        if not ids:
            continue
        a, b, p = ids
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        ans = orientation(pts[a], pts[b], pts[p])
        if ans == want:
            return query_result("orientation", "choice", ans, additions,
                f"Where is point {p} relative to directed line {a}{b}?",
                "Answer is one of: left, right, on.", f"orientation:{ans}")
    return None


def query_collinear(scene, cfg):
    want = random.choice(["yes", "no"])
    for _ in range(cfg.max_tries):
        u, t = rand_vector(cfg.coord_abs), rand_frac(cfg.max_interp_den, False)
        h = 1
        side = 0 if want == "yes" else random.choice([-h, h])
        rel = scale_points([Point(0, 0), u, Point(t*u.x-side*u.y, t*u.y+side*u.x)], cfg)
        ids, additions = local_ids(scene, rel, cfg)
        if not ids:
            continue
        a, b, c = ids
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        ans = "yes" if cross(pts[a], pts[b], pts[c]) == 0 else "no"
        if ans == want:
            return query_result("collinear", "choice", ans.capitalize(), additions,
                f"Are points {a}, {b}, and {c} collinear?", "Answer is either Yes or No.", f"collinear:{ans}")
    return None


def query_line_relation(scene, cfg):
    want = random.choice(["parallel", "perpendicular", "neither"])
    for _ in range(cfg.max_tries):
        u, w = rand_vector(cfg.coord_abs), rand_vector(cfg.coord_abs)
        if u.x*w.y == u.y*w.x:
            continue
        k = rand_nonzero(-cfg.max_vector_scale, cfg.max_vector_scale)
        if want == "parallel":
            v = Point(k*u.x, k*u.y)
        elif want == "perpendicular":
            v = Point(-k*u.y, k*u.x)
        else:
            v = rand_vector(cfg.coord_abs)
            if u.x*v.y == u.y*v.x or u.x*v.x + u.y*v.y == 0:
                continue
        rel = scale_points([Point(0, 0), u, w, Point(w.x+v.x, w.y+v.y)], cfg)
        ids, additions = local_ids(scene, rel, cfg)
        if not ids:
            continue
        a, b, c, d = ids
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        # School-geometry parallel lines are distinct; coincident lines are excluded.
        if cross(pts[a], pts[b], pts[c]) == 0:
            continue
        ans = line_relation(pts[a], pts[b], pts[c], pts[d])
        if ans == want:
            return query_result("line_relation", "choice", ans, additions,
                f"What is the relation between lines {a}{b} and {c}{d}?",
                "Answer is one of: parallel, perpendicular, neither.", f"line_relation:{ans}")
    return None


def query_line_intersection(scene, cfg):
    want = random.choice(["point", "none"])
    for _ in range(cfg.max_tries):
        u = rand_vector(cfg.coord_abs)
        if want == "none":
            w = rand_vector(cfg.coord_abs)
            if u.x*w.y == u.y*w.x:
                continue
            k = rand_nonzero(-cfg.max_vector_scale, cfg.max_vector_scale)
            t = rand_frac(cfg.max_interp_den, False)
            W = Point(t*w.x, t*w.y)
            rel = [Point(0, 0), u, W, Point(W.x+k*u.x, W.y+k*u.y)]
        else:
            v = rand_vector(cfg.coord_abs)
            if u.x*v.y == u.y*v.x:
                continue
            t, s = rand_frac(cfg.max_interp_den, False), rand_frac(cfg.max_interp_den, False)
            rel = [Point(t*u.x, t*u.y), Point((t+1)*u.x, (t+1)*u.y),
                   Point(s*v.x, s*v.y), Point((s+1)*v.x, (s+1)*v.y)]
        ids, additions = local_ids(scene, scale_points(rel, cfg), cfg)
        if not ids:
            continue
        a, b, c, d = ids
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        xs = Line(pts[a], pts[b]).intersection(Line(pts[c], pts[d]))
        if want == "none" and xs:
            continue
        if want == "point" and (len(xs) != 1 or not isinstance(xs[0], Point) or not small_point(xs[0], cfg)):
            continue
        P = xs[0] if xs else None
        return query_result("line_intersection", "point_or_none", "none" if P is None else pstr(P), additions,
            f"What is the intersection point of lines {a}{b} and {c}{d}?",
            "Answer is a coordinate pair (e.g., (2, -1/3)), or none.", f"line_intersection:{want}")
    return None


def query_segment_intersection(scene, cfg):
    families = {
        "yes": ["proper", "endpoint", "t_junction", "overlap"],
        "no": ["collinear_disjoint", "parallel_separated", "outside_both"],
    }
    want = random.choice(["yes", "no"])
    subtype = random.choice(families[want])
    for _ in range(cfg.max_tries):
        r = [sp.Rational(random.randint(1, cfg.max_interp_den), random.randint(2, cfg.max_interp_den)) for _ in range(4)]
        a0, b0, c0, d0 = [x + 1 for x in r]
        if subtype == "proper":
            coords, refs = [(-a0, 0), (b0, 0), (0, -c0), (0, d0)], (0, 1, 2, 3)
        elif subtype == "endpoint":
            coords, refs = [(-a0, 0), (0, 0), (c0, d0), (b0, -c0)], (0, 1, 1, 2)
        elif subtype == "t_junction":
            coords, refs = [(-a0, 0), (b0, 0), (0, 0), (0, d0)], (0, 1, 2, 3)
        elif subtype == "overlap":
            coords, refs = [(0, 0), (a0+b0+c0, 0), (a0, 0), (a0+b0, 0)], (0, 1, 2, 3)
        elif subtype == "collinear_disjoint":
            coords, refs = [(0, 0), (a0, 0), (a0+b0, 0), (a0+b0+c0, 0)], (0, 1, 2, 3)
        elif subtype == "parallel_separated":
            coords, refs = [(0, 0), (a0, 0), (0, c0), (b0, c0)], (0, 1, 2, 3)
        else:
            # Supporting lines meet at the origin, outside both positive-ray segments.
            coords, refs = [(a0, 0), (a0+b0, 0), (0, c0), (0, c0+d0)], (0, 1, 2, 3)
        rel = affine_points(coords, cfg)
        if rel is None:
            continue
        ids, additions = local_ids(scene, rel, cfg)
        if not ids:
            continue
        a, b, c, d = (ids[i] for i in refs)
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        ans = "yes" if Segment(pts[a], pts[b]).intersection(Segment(pts[c], pts[d])) else "no"
        if ans == want:
            return query_result("segment_intersection", "choice", ans.capitalize(), additions,
                f"Do segments {a}{b} and {c}{d} intersect?",
                "Endpoint contact and collinear overlap count as intersection. Answer is either Yes or No.",
                f"segment_intersection:{ans}", subtype)
    return None


def query_between(scene, cfg):
    want = random.choice(["yes", "no"])
    for _ in range(cfg.max_tries):
        u, t = rand_vector(cfg.coord_abs), frac_scale(cfg)
        if want == "yes":
            P = Point(t*u.x, t*u.y)
        else:
            h = random.choice([-1, 1]) * min(t, 1 - t)
            P = Point(t*u.x-h*u.y, t*u.y+h*u.x)
        ids, additions = local_ids(scene, scale_points([Point(0, 0), u, P], cfg), cfg)
        if not ids:
            continue
        a, b, p = ids
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        ans = "yes" if on_segment(pts[a], pts[b], pts[p]) else "no"
        if ans == want:
            return query_result("between", "choice", ans.capitalize(), additions,
                f"Is point {p} on segment {a}{b}?", "Endpoint contact counts. Answer is either Yes or No.",
                f"between:{ans}")
    return None


def query_angle_type(scene, cfg):
    want = random.choice(["acute", "right", "obtuse"])
    for _ in range(cfg.max_tries):
        u = rand_vector(cfg.coord_abs)
        if want == "right":
            k = rand_nonzero(-cfg.max_vector_scale, cfg.max_vector_scale)
            v = Point(-k*u.y, k*u.x)
        else:
            v = rand_vector(cfg.coord_abs)
            d = u.x*v.x + u.y*v.y
            if d == 0 or (want == "acute") != (d > 0):
                continue
        ids, additions = local_ids(scene, scale_points([u, Point(0, 0), v], cfg), cfg)
        if not ids:
            continue
        a, b, c = ids
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        if cross(pts[a], pts[b], pts[c]) == 0:
            continue
        ans = angle_type(pts[a], pts[b], pts[c])
        if ans == want:
            return query_result("angle_type", "choice", ans, additions,
                f"What type of angle is angle {a}{b}{c}?",
                "Answer is one of: acute, right, obtuse.", f"angle_type:{ans}")
    return None


def query_inside_triangle(scene, cfg):
    want = random.choice(["inside", "outside", "boundary"])
    for _ in range(cfg.max_tries):
        A, B, C = Point(0, 0), rand_vector(cfg.coord_abs), rand_vector(cfg.coord_abs)
        if cross(A, B, C) == 0:
            continue
        den = random.randint(3, cfg.max_interp_den)
        subtype = None
        vertex = want == "boundary" and random.random() < 0.2
        if want == "inside":
            a = random.randint(1, den - 2)
            b = random.randint(1, den - a - 1)
            weights = [a, b, den - a - b]
        elif vertex:
            j = random.randrange(3)
            weights = [int(i == j) for i in range(3)]
            den = 1
            subtype = "vertex"
        elif want == "boundary":
            j = random.randrange(3)
            a = random.randint(1, den - 1)
            weights = [a, den - a]
            weights.insert(j, 0)
            subtype = "edge"
        else:
            j = random.randrange(3)
            a = random.randint(1, max(1, den // 3))
            b = random.randint(1, den + a - 1)
            weights = [b, den + a - b]
            weights.insert(j, -a)
        P = Point(sum(w*Q.x for w, Q in zip(weights, (A, B, C)))/den,
                  sum(w*Q.y for w, Q in zip(weights, (A, B, C)))/den)
        rel = [A, B, C, rand_vector(cfg.coord_abs)] if vertex else [A, B, C, P]
        ids, additions = local_ids(scene, scale_points(rel, cfg), cfg)
        if not ids:
            continue
        a, b, c = ids[:3]
        p = ids[j] if vertex else ids[3]
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        ans = triangle_position(pts[a], pts[b], pts[c], pts[p])
        if ans == want:
            return query_result("inside_triangle", "choice", ans, additions,
                f"Where is point {p} relative to triangle {a}{b}{c}?",
                "Boundary includes edges and vertices. Answer is one of: inside, outside, boundary.",
                f"inside_triangle:{ans}", subtype)
    return None


def query_closer(scene, cfg):
    want = random.choice(["first", "second", "tie"])
    for _ in range(cfg.max_tries):
        u = rand_vector(cfg.coord_abs)
        if want == "tie":
            variants = [Point(-u.y, u.x), Point(u.y, -u.x), Point(-u.x, u.y), Point(u.x, -u.y)]
            choices = [v for v in variants if v != u]
            A, B = u, random.choice(choices)
        else:
            v = rand_vector(cfg.coord_abs)
            da, db = dsq(Point(0, 0), u), dsq(Point(0, 0), v)
            if da == db:
                continue
            A, B = (u, v) if (want == "first") == (da < db) else (v, u)
        ids, additions = local_ids(scene, scale_points([Point(0, 0), A, B], cfg), cfg)
        if not ids:
            continue
        p, a, b = ids
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        da, db = dsq(pts[p], pts[a]), dsq(pts[p], pts[b])
        ans = a if da < db else b if db < da else "tie"
        expected = "tie" if want == "tie" else a if want == "first" else b
        if ans != expected:
            continue
        return query_result("closer", "label_or_tie", ans, additions,
            f"Which point is closer to {p}: {a} or {b}?", f"Answer is one of: {a}, {b}, tie.",
            f"closer:{want}")
    return None


def query_x_order(scene, cfg):
    ids = sample_ids(scene, min(4, len(scene["points"])), cfg)
    if not ids:
        return None
    ans = sorted(ids, key=lambda i: (scene["points"][i].x, scene["points"][i].y, i))
    return edict(
        type="x_order",
        kind="labels",
        answer=ans,
        additions=[],
        question=f"Order points {', '.join(ids)} by increasing x-coordinate, breaking ties by increasing y-coordinate.",
        instruction="Answer with comma-separated labels, for example A,C,B,D.",
        balance="x_order",
    )


QUERIES = {
    "orientation": query_orientation,
    "collinear": query_collinear,
    "line_relation": query_line_relation,
    "line_intersection": query_line_intersection,
    "segment_intersection": query_segment_intersection,
    "between": query_between,
    "angle_type": query_angle_type,
    "inside_triangle": query_inside_triangle,
    "closer": query_closer,
    "x_order": query_x_order,
}


@dataclass
class PlanarGeometryRelationsConfig(Config):
    n_base_points: int = 5
    n_constructed_points: int = 2
    coord_abs: int = 5
    max_den: int = 80
    max_num: int = 300
    max_tries: int = 100
    max_interp_den: int = 9
    max_vector_scale: int = 4
    constructed_operand_weight: float = 3.0
    constructed_operand_prob: float = 0.65
    construction_execution: float = 0.5
    query_types: list = field(default_factory=lambda: list(QUERIES))

    def apply_difficulty(self, level):
        self.n_base_points = sround(self.n_base_points + 0.35 * level)
        self.n_constructed_points = sround(self.n_constructed_points + 0.9 * level)
        self.coord_abs = sround(self.coord_abs + 1.5 * level)
        self.max_den = sround(self.max_den + 16 * level)
        self.max_num = sround(self.max_num + 60 * level)
        self.max_interp_den = sround(self.max_interp_den + 0.8 * level)
        self.max_vector_scale = sround(self.max_vector_scale + 0.25 * level)

class PlanarGeometryRelations(Task):
    summary = "Answer geometry queries about point intersections, angles, and distances."

    def __init__(self, config=None, **kwargs):
        super().__init__(config=config or PlanarGeometryRelationsConfig(), **kwargs)
        self.balancing_key_ratio = 0.18

    def generate_entry(self):
        query_types = [q for q in self.config.query_types if q in QUERIES] or list(QUERIES)

        for _ in range(self.config.max_tries):
            scene = make_scene(self.config)
            construction_execution = (
                bool(scene["definitions"])
                and random.random() < self.config.construction_execution
            )
            query_config = copy(self.config)
            if construction_execution:
                query_config.constructed_operand_prob = 1.0

            for name in random.sample(query_types, len(query_types)):
                query = QUERIES[name](scene, query_config)
                if query is None:
                    continue
                referenced = set(ID_RE.findall(query.question))
                if construction_execution and not referenced.intersection(scene["definitions"]):
                    continue

                rendered = render(scene, query, construction_execution=construction_execution)
                metadata = edict(
                    points=rendered.points,
                    definitions=rendered.definitions,
                    query=rendered.query,
                    instruction=rendered.instruction,
                    query_type=rendered.query_type,
                    answer_kind=rendered.answer_kind,
                    balance=rendered.balance,
                    construction_family=rendered.construction_family,
                    internal_query=rendered.internal_query,
                    construction_execution=construction_execution,
                )
                return Entry(metadata=metadata, answer=rendered.answer)

        raise RuntimeError("Could not generate a valid planar geometry problem after bounded attempts")

    def render_prompt(self, metadata):
        points = "; ".join(f"{a}={metadata.points[a]}" for a in sorted(metadata.points))
        lines = [f"Given points: {points}."]

        if metadata.definitions:
            lines.append("Definitions: " + " ".join(metadata.definitions))

        lines += [
            "Question: " + metadata.query,
            metadata.instruction,
        ]
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        entry.metadata = edict(entry['metadata'])
        if answer is None:
            return 0.0

        kind = entry.metadata.answer_kind
        ref = entry.answer

        if kind == "point_or_none":
            if clean(ref) == "none" or clean(answer) == "none":
                return float(clean(answer) == clean(ref))
            got, expected = parse_point(answer), parse_point(ref)
            return float(got is not None and got == expected)

        if kind in {"label", "label_or_tie"}:
            return float(clean(answer) == "tie") if clean(ref) == "tie" else float(clean_labels(answer) == clean_labels(ref))

        if kind == "labels":
            return float(clean_labels(answer) == clean_labels(ref))

        return float(clean(answer) == clean(ref))

    def balancing_key(self, problem):
        return problem.metadata.balance

    def deduplication_key(self, problem):
        return repr((
            tuple(problem.metadata.points.items()),
            tuple(problem.metadata.definitions),
            problem.metadata.query,
        ))
