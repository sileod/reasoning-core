import random
import re
from dataclasses import dataclass, field

import sympy as sp
from sympy.geometry import Point, Line, Segment

from reasoning_core.template import Config, Problem, Task, edict


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


def line_point(A, B, t):
    return Point(A.x + t * (B.x - A.x), A.y + t * (B.y - A.y))


def bary_point(A, B, C, den):
    w = [random.randint(1, den) for _ in range(3)]
    s = sum(w)
    return Point(
        sp.Rational(w[0] * A.x + w[1] * B.x + w[2] * C.x, s),
        sp.Rational(w[0] * A.y + w[1] * B.y + w[2] * C.y, s),
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


def render(scene, query):
    points = dict(scene["points"])
    definitions = dict(scene["definitions"])

    for i, P, definition, _ in query.additions:
        points[i] = P
        if definition:
            definitions[i] = definition

    ids = list(points)
    labels = dict(zip(ids, random.sample(LABELS, len(ids))))

    shown = edict({labels[i]: pstr(points[i]) for i in sorted(ids, key=lambda x: labels[x])})
    defs = [f"{labels[i]} is {render_text(definitions[i], labels)}." for i in definitions]

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
        additions = []
        ids = sample_ids(scene, 2 if want == "on" else 3, cfg)
        if not ids:
            return None

        if want == "on":
            a, b = ids
            A, B = scene["points"][a], scene["points"][b]
            if A == B:
                continue
            p = candidate(scene, additions, line_point(A, B, rand_frac(cfg.max_interp_den, proper=False)), cfg)
            if p is None:
                continue
        else:
            a, b, p = ids

        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        if pts[a] == pts[b]:
            continue
        ans = orientation(pts[a], pts[b], pts[p])
        if ans == want:
            return edict(
                type="orientation",
                kind="choice",
                answer=ans,
                additions=additions,
                question=f"Where is point {p} relative to directed line {a}{b}?",
                instruction="Answer is one of: left, right, on.",
                balance=f"orientation:{ans}",
            )
    return None


def query_collinear(scene, cfg):
    want = random.choice(["yes", "no"])
    for _ in range(cfg.max_tries):
        additions = []
        ids = sample_ids(scene, 2 if want == "yes" else 3, cfg)
        if not ids:
            return None

        if want == "yes":
            a, b = ids
            A, B = scene["points"][a], scene["points"][b]
            if A == B:
                continue
            c = candidate(scene, additions, line_point(A, B, rand_frac(cfg.max_interp_den, proper=False)), cfg)
            if c is None:
                continue
        else:
            a, b, c = ids

        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        if len({key(pts[a]), key(pts[b]), key(pts[c])}) < 3:
            continue
        ans = "yes" if cross(pts[a], pts[b], pts[c]) == 0 else "no"
        if ans == want:
            return edict(
                type="collinear",
                kind="choice",
                answer=ans,
                additions=additions,
                question=f"Are points {a}, {b}, and {c} collinear?",
                instruction="Answer is either yes or no.",
                balance=f"collinear:{ans}",
            )
    return None


def query_line_relation(scene, cfg):
    want = random.choice(["parallel", "perpendicular", "neither"])
    for _ in range(cfg.max_tries):
        additions = []

        if want in {"parallel", "perpendicular"}:
            ids = sample_ids(scene, 3, cfg)
            if not ids:
                return None
            a, b, c = ids
            A, B, C = (scene["points"][i] for i in ids)
            if A == B:
                continue
            ux, uy = B.x - A.x, B.y - A.y
            k = rand_nonzero(-cfg.max_vector_scale, cfg.max_vector_scale)
            vx, vy = (k * ux, k * uy) if want == "parallel" else (-k * uy, k * ux)
            d = candidate(scene, additions, Point(C.x + vx, C.y + vy), cfg)
            if d is None:
                continue
        else:
            ids = sample_ids(scene, 4, cfg)
            if not ids:
                return None
            a, b, c, d = ids

        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        if pts[a] == pts[b] or pts[c] == pts[d]:
            continue
        ans = line_relation(pts[a], pts[b], pts[c], pts[d])
        if ans == want:
            return edict(
                type="line_relation",
                kind="choice",
                answer=ans,
                additions=additions,
                question=f"What is the relation between lines {a}{b} and {c}{d}?",
                instruction="Answer is one of: parallel, perpendicular, neither.",
                balance=f"line_relation:{ans}",
            )
    return None


def query_line_intersection(scene, cfg):
    want = random.choice(["point", "none"])
    for _ in range(cfg.max_tries):
        additions = []

        if want == "none":
            ids = sample_ids(scene, 3, cfg)
            if not ids:
                return None
            a, b, c = ids
            A, B, C = (scene["points"][i] for i in ids)
            if A == B:
                continue
            k = rand_nonzero(-cfg.max_vector_scale, cfg.max_vector_scale)
            d = candidate(scene, additions, Point(C.x + k * (B.x - A.x), C.y + k * (B.y - A.y)), cfg)
            if d is None:
                continue
            P = None
        else:
            ids = sample_ids(scene, 4, cfg)
            if not ids:
                return None
            a, b, c, d = ids
            P = line_intersection(*(scene["points"][i] for i in ids))
            if P is None or not small_point(P, cfg):
                continue

        return edict(
            type="line_intersection",
            kind="point_or_none",
            answer="none" if P is None else pstr(P),
            additions=additions,
            question=f"What is the intersection point of lines {a}{b} and {c}{d}?",
            instruction="Answer is a coordinate pair (e.g., (2, -1/3)), or none.",
            balance=f"line_intersection:{'none' if P is None else 'point'}",
        )
    return None


def query_segment_intersection(scene, cfg):
    want = random.choice(["yes", "no"])
    for _ in range(cfg.max_tries):
        additions = []

        if want == "yes":
            O = rand_point(cfg.coord_abs)
            u = Point(rand_nonzero(-cfg.coord_abs - 1, cfg.coord_abs + 1), random.randint(-cfg.coord_abs, cfg.coord_abs))
            v = Point(random.randint(-cfg.coord_abs, cfg.coord_abs), rand_nonzero(-cfg.coord_abs - 1, cfg.coord_abs + 1))
            if cross(Point(0, 0), u, v) == 0:
                continue
            su, sv = random.randint(1, 3), random.randint(1, 3)
            ids = [
                candidate(scene, additions, Point(O.x + su * u.x, O.y + su * u.y), cfg),
                candidate(scene, additions, Point(O.x - su * u.x, O.y - su * u.y), cfg),
                candidate(scene, additions, Point(O.x + sv * v.x, O.y + sv * v.y), cfg),
                candidate(scene, additions, Point(O.x - sv * v.x, O.y - sv * v.y), cfg),
            ]
            if any(i is None for i in ids):
                continue
            a, b, c, d = ids
        else:
            ids = sample_ids(scene, 4, cfg)
            if not ids:
                return None
            a, b, c, d = ids

        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        if pts[a] == pts[b] or pts[c] == pts[d]:
            continue
        ans = "yes" if Segment(pts[a], pts[b]).intersection(Segment(pts[c], pts[d])) else "no"
        if ans == want:
            return edict(
                type="segment_intersection",
                kind="choice",
                answer=ans,
                additions=additions,
                question=f"Do segments {a}{b} and {c}{d} intersect?",
                instruction="Answer is either yes or no.",
                balance=f"segment_intersection:{ans}",
            )
    return None


def query_between(scene, cfg):
    want = random.choice(["yes", "no"])
    for _ in range(cfg.max_tries):
        additions = []
        ids = sample_ids(scene, 2 if want == "yes" else 3, cfg)
        if not ids:
            return None

        if want == "yes":
            a, b = ids
            A, B = scene["points"][a], scene["points"][b]
            if A == B:
                continue
            p = candidate(scene, additions, line_point(A, B, rand_frac(cfg.max_interp_den, proper=True)), cfg)
            if p is None:
                continue
        else:
            a, b, p = ids

        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        if pts[a] == pts[b]:
            continue
        ans = "yes" if on_segment(pts[a], pts[b], pts[p]) else "no"
        if ans == want:
            return edict(
                type="between",
                kind="choice",
                answer=ans,
                additions=additions,
                question=f"Is point {p} on segment {a}{b}?",
                instruction="Answer is either yes or no.",
                balance=f"between:{ans}",
            )
    return None


def query_angle_type(scene, cfg):
    want = random.choice(["acute", "right", "obtuse"])
    for _ in range(cfg.max_tries):
        additions = []

        if want == "right":
            ids = sample_ids(scene, 2, cfg)
            if not ids:
                return None
            b, a = ids
            B, A = scene["points"][b], scene["points"][a]
            if A == B:
                continue
            ux, uy = A.x - B.x, A.y - B.y
            k = rand_nonzero(-cfg.max_vector_scale, cfg.max_vector_scale)
            c = candidate(scene, additions, Point(B.x - k * uy, B.y + k * ux), cfg)
            if c is None:
                continue
        else:
            ids = sample_ids(scene, 3, cfg)
            if not ids:
                return None
            a, b, c = ids

        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        if pts[a] == pts[b] or pts[c] == pts[b]:
            continue
        ans = angle_type(pts[a], pts[b], pts[c])
        if ans == want:
            return edict(
                type="angle_type",
                kind="choice",
                answer=ans,
                additions=additions,
                question=f"What type of angle is angle {a}{b}{c}?",
                instruction="Answer is one of: acute, right, obtuse.",
                balance=f"angle_type:{ans}",
            )
    return None


def query_inside_triangle(scene, cfg):
    want = random.choice(["inside", "outside", "boundary"])
    for _ in range(cfg.max_tries):
        additions = []
        ids = sample_ids(scene, 3, cfg)
        if not ids:
            return None
        a, b, c = ids
        A, B, C = (scene["points"][i] for i in ids)
        if cross(A, B, C) == 0:
            continue

        if want == "inside":
            p = candidate(scene, additions, bary_point(A, B, C, cfg.max_interp_den), cfg)
            if p is None:
                continue
        elif want == "boundary":
            U, V = random.choice([(A, B), (B, C), (C, A)])
            p = candidate(scene, additions, line_point(U, V, rand_frac(cfg.max_interp_den, proper=True)), cfg)
            if p is None:
                continue
        else:
            candidates = [x for x in scene["points"] if x not in {a, b, c}]
            if not candidates:
                continue
            p = random.choice(candidates)

        if p in {a, b, c}:
            continue
        pts = dict(scene["points"], **{i: P for i, P, _, _ in additions})
        ans = triangle_position(pts[a], pts[b], pts[c], pts[p])
        if ans == want:
            return edict(
                type="inside_triangle",
                kind="choice",
                answer=ans,
                additions=additions,
                question=f"Where is point {p} relative to triangle {a}{b}{c}?",
                instruction="Answer is one of: inside, outside, boundary.",
                balance=f"inside_triangle:{ans}",
            )
    return None


def query_closer(scene, cfg):
    want = random.choice(["first", "second", "tie"])
    for _ in range(cfg.max_tries):
        additions = []

        if want == "tie":
            ids = sample_ids(scene, 2, cfg)
            if not ids:
                return None
            a, b = ids
            A, B = scene["points"][a], scene["points"][b]
            if A == B:
                continue
            M = Segment(A, B).midpoint
            ux, uy = B.x - A.x, B.y - A.y
            k = rand_frac(cfg.max_interp_den, proper=False)
            p = candidate(scene, additions, Point(M.x - k * uy, M.y + k * ux), cfg)
            if p is None:
                continue
            ans = "tie"
        else:
            ids = sample_ids(scene, 3, cfg)
            if not ids:
                return None
            p, a, b = ids
            P, A, B = (scene["points"][i] for i in ids)
            if A == B:
                continue
            da, db = dsq(P, A), dsq(P, B)
            ans = a if da < db else b if db < da else "tie"
            if (want == "first" and ans != a) or (want == "second" and ans != b):
                continue

        return edict(
            type="closer",
            kind="label_or_tie",
            answer=ans,
            additions=additions,
            question=f"Which point is closer to {p}: {a} or {b}?",
            instruction=f"Answer is one of: {a}, {b}, tie.",
            balance=f"closer:{'tie' if ans == 'tie' else 'label'}",
        )
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
    query_types: list = field(default_factory=lambda: list(QUERIES))

    def update(self, c):
        self.n_base_points += 0.35 * c
        self.n_constructed_points += 0.9 * c
        self.coord_abs += 1.5 * c
        self.max_den += 16 * c
        self.max_num += 60 * c
        self.max_interp_den += 0.8 * c
        self.max_vector_scale += 0.25 * c

    def apply_difficulty(self, level):
        self.n_base_points += 0.35 * level
        self.n_constructed_points += 0.9 * level
        self.coord_abs += 1.5 * level
        self.max_den += 16 * level
        self.max_num += 60 * level
        self.max_interp_den += 0.8 * level
        self.max_vector_scale += 0.25 * level

class PlanarGeometryRelations(Task):

    def __init__(self, config=None, **kwargs):
        super().__init__(config=config or PlanarGeometryRelationsConfig(), **kwargs)
        self.balancing_key_ratio = 0.18

    def generate(self):
        query_types = [q for q in self.config.query_types if q in QUERIES] or list(QUERIES)

        for _ in range(self.config.max_tries):
            scene = make_scene(self.config)
            for name in random.sample(query_types, len(query_types)):
                query = QUERIES[name](scene, self.config)
                if query is None:
                    continue

                rendered = render(scene, query)
                metadata = edict(
                    points=rendered.points,
                    definitions=rendered.definitions,
                    query=rendered.query,
                    instruction=rendered.instruction,
                    query_type=rendered.query_type,
                    answer_kind=rendered.answer_kind,
                    balance=rendered.balance,
                    internal_query=rendered.internal_query,
                )
                return Problem(metadata=metadata, answer=rendered.answer)

        return None

    def prompt(self, metadata):
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
