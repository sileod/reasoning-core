import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'convex_hull_ordering (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/convex_hull_ordering',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Answer format: return the full ordered hull vertex list as a compact string like '0,0;2,0;2,1;0,1' for all instances, with no query variant."


@dataclass
class ConvexHullOrderingConfig(Config):
    n: int = 8
    coord_range: int = 10
    collinear: float = 0.4

    def apply_difficulty(self, level):
        self.n = stochastic_rounding(8 + 3 * level)
        self.coord_range = stochastic_rounding(10 + 4 * level)
        self.collinear = min(0.7, 0.3 + 0.08 * level)


def _parse_points(s):
    pts = []
    for tok in s.split(";"):
        xs, ys = tok.split(",")
        pts.append((int(xs), int(ys)))
    return pts


_parse_eq = _parse_points


def _point_string(pts):
    return ";".join(f"{p[0]},{p[1]}" for p in pts)


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def monotone_hull(points):
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts
    lower = []
    for p in pts:
        while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    return hull


def _point_on_segment(p, a, b):
    if _cross(a, b, p) != 0:
        return False
    return min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])


def _in_hull_region(hull, p):
    if len(hull) < 3:
        return True
    for i in range(len(hull)):
        a = hull[i]
        b = hull[(i + 1) % len(hull)]
        if _cross(a, b, p) < 0:
            return False
    return True


def _canonical_ccw(hull):
    import math
    pts = sorted(set(hull))
    if len(pts) <= 2:
        return pts
    centroid = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    def angle(p):
        dx = p[0] - centroid[0]
        dy = p[1] - centroid[1]
        a = math.atan2(dy, dx)
        return (a, p[1], p[0])

    return sorted(pts, key=angle)


class ConvexHullOrdering(Task):
    summary = ("Compute the exact convex hull of finite planar point sets with collinearities, "
               "returning the canonical counterclockwise ordered list of extreme vertex x,y pairs.")
    config_cls = ConvexHullOrderingConfig

    def generate_entry(self):
        cfg = self.config
        while True:
            n = cfg.n
            pts = set()
            while len(pts) < n:
                x = random.randint(-cfg.coord_range, cfg.coord_range)
                y = random.randint(-cfg.coord_range, cfg.coord_range)
                pts.add((x, y))
            pts = list(pts)
            hull = monotone_hull(pts)
            if len(hull) < 3:
                hull = self._force_non_collinear(pts)
                if hull is None:
                    continue
            if self.config.collinear == 0:
                break
            break

        hull = sorted(set(hull))
        canon = _canonical_ccw(hull)
        if len(canon) < 3:
            canon = self._force_non_collinear(pts)
        canon = _canonical_ccw(canon)
        answer = _point_string(canon)
        self._verify(pts, canon)
        return Entry(metadata={
            "points": _point_string(pts),
            "n": n,
            "hull": answer,
        }, answer=answer)

    def _force_non_collinear(self, pts):
        for _ in range(40):
            a = random.randint(0, 1000)
            b = random.randint(0, 1000)
            p = (a - 500, b - 500)
            if _point_on_segment(p, pts[0], pts[1]) and p not in pts:
                candidate = pts + [p]
                h = monotone_hull(candidate)
                if len(h) >= 3:
                    return h
        return None

    def _verify(self, pts, canon):
        for p in canon:
            if not _in_hull_region(canon, p):
                raise RuntimeError("hull point outside")
        for q in pts:
            if not _in_hull_region(canon, q):
                raise RuntimeError("point outside hull")
        h2 = monotone_hull(pts)
        a = set(canon)
        b = set(h2)
        if a != b:
            raise RuntimeError("hull set mismatch")

    def render_prompt(self, metadata):
        return (
            "Given the planar points " + metadata["points"] + ". "
            "Compute the convex hull (the minimal convex polygon containing all points) using "
            "the monotone chain algorithm. Since points may be collinear, keep only the extreme "
            "hull vertices (intermediate points lying exactly on an edge are not hull vertices). "
            "Return the hull vertices in counterclockwise order starting from the leftmost-lowest "
            "vertex, as a compact semicolon-separated list of x,y pairs, e.g. '0,0;2,0;2,1;0,1'. "
            "The answer is this exact list."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        ans = answer.strip()
        if not ans:
            return 0.0
        try:
            parsed = _parse_points(ans)
        except Exception:
            return 0.0
        gold = _parse_points(entry.answer)
        if set(parsed) != set(gold):
            return 0.0
        canon_parsed = _canonical_ccw(parsed)
        return 1.0 if canon_parsed == gold else 0.0
