import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'exterior_meet_join (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_transfer_r4/exterior_meet_join',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def det2(a0, a1, b0, b1):
    return a0 * b1 - a1 * b0


def det3(m):
    (a, b, c), (d, e, f), (g, h, i) = m
    return (a * (e * i - f * h)
            - b * (d * i - f * g)
            + c * (d * h - e * g))


def cross3(u, v):
    return (det2(u[1], u[2], v[1], v[2]),
            -det2(u[0], u[2], v[0], v[2]),
            det2(u[0], u[1], v[0], v[1]))


def _canon(vec):
    v = list(vec)
    g = 0
    for c in v:
        g = math.gcd(g, abs(c))
    if g > 1:
        v = [c // g for c in v]
    v = tuple(v)
    if v == (0, 0, 0) or v == (0, 0, 0, 0):
        return v
    for c in v:
        if c != 0:
            if c < 0:
                v = tuple(-x for x in v)
            break
    return v


def canonical_point(vec):
    v = _canon(vec)
    if len(v) <= 3:
        return "(" + ", ".join(str(int(c)) for c in v[0:3]) + ")"
    return "(" + ", ".join(str(int(c)) for c in v[0:4]) + ")"


EMPTY = "empty"


def meet_point_line_2d(p, a, b):
    if det3((p, a, b)) == 0:
        return canonical_point(p)
    return EMPTY


def meet_line_line_2d(a, b, c, d):
    l1 = cross3(a, b)
    l2 = cross3(c, d)
    pt = cross3(l1, l2)
    return canonical_point(pt)


def meet_line_plane_3d(a, b, c, d, e):
    return canonical_point(_meet_line_plane(a, b, c, d, e))


@dataclass
class ExteriorMeetJoinV2Config(Config):
    coord_range: int = 8
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level
        self.coord_range = stochastic_rounding(6 + 2 * level)


class ExteriorMeetJoin(Task):
    summary = ("Combine projective points, lines and planes represented by coordinates, "
               "incidence blades or homogeneous equations using exterior joins and "
               "regressive meets; return the resulting subspace or a degeneracy label.")
    design_choice = ("Instances give two incidence blades (e.g., point-line, line-plane) "
                     "as index sets; solvers output the meet as a Grassmann-Cayley bracket "
                     "expression in canonical integer form, or 'empty' for no intersection.")
    config_cls = ExteriorMeetJoinV2Config
    task_version = 2

    def generate_entry(self):
        r = self.config.coord_range
        low, high = -r, r
        mode = random.choice(["pl2", "ll2", "lp3", "pl2"])
        if mode == "pl2":
            a = _rand(low, high, 3)
            b = _rand(low, high, 3)
            tries = 0
            while (a == b or _iszero(a) or _iszero(b)
                   or _iszero(cross3(a, b))) and tries < 200:
                a = _rand(low, high, 3)
                b = _rand(low, high, 3)
                tries += 1
            on = random.random() < 0.5
            if on:
                w1 = random.choice([-1, 1, 2])
                w2 = random.choice([1, 2, -1])
                p = tuple(w1 * x + w2 * y for x, y in zip(a, b))
                if _iszero(p):
                    p = tuple(x + y for x, y in zip(a, b))
                tries = 0
                while (det3((p, a, b)) != 0) and tries < 20:
                    w1 = random.choice([-1, 1, 2])
                    w2 = random.choice([1, 2, -1])
                    p = tuple(w1 * x + w2 * y for x, y in zip(a, b))
                    tries += 1
            else:
                p = _rand(low, high, 3)
                tries = 0
                while (_iszero(p) or det3((p, a, b)) == 0) and tries < 200:
                    p = _rand(low, high, 3)
                    tries += 1
            ans = meet_point_line_2d(p, a, b)
            meta = {"mode": "point_line_2d", "point": p, "line": (a, b),
                    "on_line": on}
        elif mode == "ll2":
            a = _rand(low, high, 3)
            b = _rand(low, high, 3)
            c = _rand(low, high, 3)
            d = _rand(low, high, 3)
            tries = 0
            while (_iszero(a) or _iszero(b) or _iszero(c) or _iszero(d)
                   or a == b or c == d) and tries < 200:
                a = _rand(low, high, 3)
                b = _rand(low, high, 3)
                c = _rand(low, high, 3)
                d = _rand(low, high, 3)
                tries += 1
            pt = _canon(cross3(cross3(a, b), cross3(c, d)))
            tries = 0
            while _iszero(pt) and tries < 200:
                c = _rand(low, high, 3)
                d = _rand(low, high, 3)
                pt = _canon(cross3(cross3(a, b), cross3(c, d)))
                tries += 1
            ans = canonical_point(pt)
            meta = {"mode": "line_line_2d", "lines": ((a, b), (c, d))}
        else:
            a = _rand(low, high, 4)
            b = _rand(low, high, 4)
            c = _rand(low, high, 4)
            d = _rand(low, high, 4)
            e = _rand(low, high, 4)
            tries = 0
            while (_iszero(a) or _iszero(b) or _iszero(c) or _iszero(d)
                   or _iszero(e) or a == b or c == d or d == e or c == e
                   or _plane_normal(c, d, e) is None) and tries < 400:
                a = _rand(low, high, 4)
                b = _rand(low, high, 4)
                c = _rand(low, high, 4)
                d = _rand(low, high, 4)
                e = _rand(low, high, 4)
                tries += 1
            pt = _meet_line_plane(a, b, c, d, e)
            tries = 0
            while _iszero(pt) and tries < 400:
                a = _rand(low, high, 4)
                b = _rand(low, high, 4)
                pt = _meet_line_plane(a, b, c, d, e)
                tries += 1
            if _iszero(pt):
                meta = {"mode": "line_plane_3d", "line": (a, b),
                        "plane": (c, d, e), "answer": EMPTY}
                return Entry(metadata=meta, answer=EMPTY)
            ans = canonical_point(pt)
            meta = {"mode": "line_plane_3d", "line": (a, b),
                    "plane": (c, d, e)}

        meta["answer"] = ans
        return Entry(metadata=meta, answer=ans)

    def render_prompt(self, metadata):
        m = metadata
        if m["mode"] == "point_line_2d":
            a, b = m["line"]
            return (f"In the projective plane, a point is a 1-blade and a line is the "
                    f"exterior join of two points. The point P = {m['point']} and the line "
                    f"L = a \u2227 b with a = {a}, b = {b} are given. Their regressive meet "
                    f"(intersection subspace) is the point P itself when it lies on L, "
                    f"otherwise it is empty. Say whether the meet exists; if it does, give the "
                    f"meet point in canonical integer form (coordinates divided by gcd, first "
                    f"nonzero entry positive), e.g. (2, -3, 1); otherwise answer 'empty'.")
        if m["mode"] == "line_line_2d":
            (a, b), (c, d) = m["lines"]
            return (f"In the projective plane, each line is the exterior join of two points. "
                    f"Line L1 = {a} \u2227 {b} and line L2 = {c} \u2227 {d} are given. "
                    f"Their regressive meet is their intersection point, given by the "
                    f"Grassmann-Cayley bracket expression ([a b d] c - [a b c] d) where "
                    f"[x y z] is the determinant det(x,y,z). Give the meet point in canonical "
                    f"integer form (coordinates divided by gcd, first nonzero entry positive), "
                    f"e.g. (2, -3, 1).")
        a, b = m["line"]
        c, d, e = m["plane"]
        return (f"In projective 3-space, a line is the exterior join of two points and a "
                f"plane is the join of three points. Line L = {a} \u2227 {b} and plane "
                f"\u03a0 = {c} \u2227 {d} \u2227 {e} are given. Their regressive meet is "
                f"the intersection point, given by the Grassmann-Cayley bracket expression "
                f"([b c d e] a - [a c d e] b). Give the meet point in canonical integer form "
                f"(coordinates divided by gcd, first nonzero entry positive), e.g. (1, -2, 3, 4).")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = entry.answer
        if answer.strip().replace(" ", "") == gold.strip().replace(" ", ""):
            return 1.0
        if gold == EMPTY and answer.strip().lower() == EMPTY:
            return 1.0
        return 0.0


def _iszero(v):
    return all(c == 0 for c in v)


def _rand(low, high, n):
    return tuple(random.randint(low, high) for _ in range(n))


def _plane_normal(c, d, e):
    v = [0, 0, 0, 0]
    for j in range(4):
        minor = [row for row in (c, d, e)]
        col = j
        sub = []
        for row in minor:
            sub.append(tuple(row[k] for k in range(4) if k != col))
        v[j] = det3(sub)
        if j % 2 == 1:
            v[j] = -v[j]
    if all(x == 0 for x in v):
        return None
    return tuple(v)


def _meet_line_plane(a, b, c, d, e):
    pi = _plane_normal(c, d, e)
    if pi is None:
        return (0, 0, 0, 0)
    da = sum(x * y for x, y in zip(pi, a))
    db = sum(x * y for x, y in zip(pi, b))
    pt = tuple(db * x - da * y for x, y in zip(a, b))
    return tuple(int(z) for z in pt)
