import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _cross(ax, ay, bx, by, cx, cy):
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def _on_seg(ax, ay, bx, by, x, y):
    return (_cross(ax, ay, bx, by, x, y) == 0
            and min(ax, bx) <= x <= max(ax, bx)
            and min(ay, by) <= y <= max(ay, by))


def _seg_proper_intersect(ax, ay, bx, by, cx, cy, dx, dy):
    d1 = _cross(ax, ay, bx, by, cx, cy)
    d2 = _cross(ax, ay, bx, by, dx, dy)
    d3 = _cross(cx, cy, dx, dy, ax, ay)
    d4 = _cross(cx, cy, dx, dy, bx, by)
    return d1 * d2 < 0 and d3 * d4 < 0


def _is_simple(poly):
    m = len(poly)
    if m < 3:
        return False
    if len(set(poly)) != m:
        return False
    for i in range(m):
        j = (i + 1) % m
        for k in range(m):
            l = (k + 1) % m
            if k == i or k == j or l == i or l == j:
                continue
            if _seg_proper_intersect(poly[i][0], poly[i][1], poly[j][0], poly[j][1],
                                     poly[k][0], poly[k][1], poly[l][0], poly[l][1]):
                return False
    return True


def _signed_area(poly):
    s = 0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def _pts_strictly_inside_tri(ax, ay, bx, by, cx, cy, pts):
    s0 = _cross(ax, ay, bx, by, cx, cy)
    if s0 <= 0:
        return False
    for (x, y) in pts:
        if (_cross(ax, ay, bx, by, x, y) > 0
                and _cross(bx, by, cx, cy, x, y) > 0
                and _cross(cx, cy, ax, ay, x, y) > 0):
            return True
    return False


def _diag_valid_current(pts, cur, e0, e1):
    m = len(cur)
    if m < 3:
        return False
    q0 = cur.index(e0)
    q1 = cur.index(e1)
    if abs(q0 - q1) == 1 or abs(q0 - q1) == m - 1:
        return False
    ax, ay = pts[e0]
    cx, cy = pts[e1]
    for o in cur:
        x, y = pts[o]
        if o not in (e0, e1) and _on_seg(ax, ay, cx, cy, x, y):
            return False
    for i in range(m):
        j = (i + 1) % m
        a = cur[i]
        b = cur[j]
        if a in (e0, e1) or b in (e0, e1):
            continue
        if _seg_proper_intersect(ax, ay, cx, cy,
                                 pts[a][0], pts[a][1], pts[b][0], pts[b][1]):
            return False
    return True


def _clip(points_list):
    pts = [tuple(p) for p in points_list]
    n = len(pts)
    cur = list(range(n))
    tips = []
    diags = []
    while len(cur) > 3:
        chosen = -1
        for p in range(len(cur)):
            pv = cur[(p - 1) % len(cur)]
            tv = cur[p]
            nv = cur[(p + 1) % len(cur)]
            ax, ay = pts[pv]
            bx, by = pts[tv]
            cx, cy = pts[nv]
            if _cross(ax, ay, bx, by, cx, cy) <= 0:
                continue
            if not _diag_valid_current(pts, cur, pv, nv):
                continue
            others = [pts[o] for o in cur if o not in (pv, tv, nv)]
            if _pts_strictly_inside_tri(ax, ay, bx, by, cx, cy, others):
                continue
            chosen = p
            break
        if chosen == -1:
            return None
        tips.append(cur[chosen])
        d0 = cur[(chosen - 1) % len(cur)]
        d1 = cur[(chosen + 1) % len(cur)]
        diags.append((min(d0, d1), max(d0, d1)))
        cur.pop(chosen)
    final = sorted(cur)
    return tips, diags, final


def _make_polygon(cfg):
    n = random.randint(cfg.min_vert, cfg.max_vert)
    mc = cfg.max_coord
    for _ in range(200):
        pts = set()
        while len(pts) < n and len(pts) + 0 < 2000:
            pts.add((random.randint(-mc, mc), random.randint(-mc, mc)))
        if len(pts) < n:
            continue
        pts = list(pts)
        pivot = min(pts, key=lambda p: (p[1], p[0]))
        others = [p for p in pts if p != pivot]

        def ang(p_):
            import math
            return math.atan2(p_[1] - pivot[1], p_[0] - pivot[0])

        others.sort(key=lambda p: (ang(p),
                                   (p[0] - pivot[0]) ** 2 + (p[1] - pivot[1]) ** 2))
        poly = [pivot] + others
        area = _signed_area(poly)
        if area == 0:
            continue
        if area < 0:
            poly.reverse()
        poly = _maybe_collinear(poly, cfg)
        if _is_simple(poly):
            return poly
    raise RuntimeError("ear_clipping_triangulation: could not build a simple polygon")


def _maybe_collinear(poly, cfg):
    res = list(poly)
    setp = set(res)
    inserted = 0
    i = 0
    guard = 0
    while i < len(res) - 1 and inserted < cfg.max_insert and guard < 200:
        guard += 1
        ax, ay = res[i]
        bx, by = res[i + 1]
        dx = bx - ax
        dy = by - ay
        if dx == 0 and dy == 0:
            i += 1
            continue
        if dx % 2 == 0 and dy % 2 == 0:
            mx = ax + dx // 2
            my = ay + dy // 2
            if (mx, my) not in setp:
                res.insert(i + 1, (mx, my))
                setp.add((mx, my))
                inserted += 1
                i += 1
        i += 1
    return res


@dataclass
class EarClippingConfig(Config):
    min_vert: int = 6
    max_vert: int = 7
    max_coord: int = 8
    collinear_prob: float = 0.3
    max_insert: int = 1

    def apply_difficulty(self, level):
        self.min_vert = 6 + 2 * level
        self.max_vert = 7 + 3 * level
        self.max_coord = 8 + 6 * level
        self.collinear_prob = min(0.3 + 0.05 * level, 0.6)
        self.max_insert = 1 + level


class EarClippingTriangulation(Task):
    summary = ("Triangulate simple CCW polygon chains with integer coordinates by ear clipping, "
               "cutting the first valid strictly-convex ear under a tolerance-free orientation "
               "sign test (collinear vertices are permitted but never ears), reporting the "
               "ordered ear-tip indices and the resulting diagonals.")
    design_choice = ("Represent polygon vertices as integer coordinates and compute ear validity "
                     "via orientation signs, with collinear ears allowed only if they are strictly "
                     "convex under a tolerance-free sign test.")
    config_cls = EarClippingConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(200):
            poly = _make_polygon(cfg)
            out = _clip(poly)
            if out is None:
                continue
            tips, diags, final = out
            n = len(poly)
            if len(tips) != n - 3 or len(diags) != n - 3:
                continue
            if len(set(tips)) != len(tips):
                continue
            if set(tips) & set(final):
                continue
            if len(final) != 3:
                continue
            remaining = set(range(n)) - set(tips)
            if remaining != set(final):
                continue
            for (a, c) in diags:
                if not (0 <= a < c < n):
                    break
            else:
                answer = "tips=" + str([int(t) for t in tips]) + " diags=" + str(
                    [(int(a), int(c)) for (a, c) in diags])
                metadata = {
                    "vertices": [[int(x), int(y)] for (x, y) in poly],
                    "tips": [int(t) for t in tips],
                    "diags": [[int(a), int(c)] for (a, c) in diags],
                    "final": [int(f) for f in final],
                }
                return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("ear_clipping_triangulation: failed to generate after bounded attempts")

    def render_prompt(self, metadata):
        lines = "\n".join(
            "{i}: ({x}, {y})".format(i=i, x=v[0], y=v[1])
            for i, v in enumerate(metadata["vertices"])
        )
        return (
            "Triangulate the simple polygon whose vertices are listed below in counterclockwise "
            "order, each as \"index: (x, y)\":\n\n"
            + lines
            + "\n\nAlgorithm (classic ear clipping): "
            "at each step consider every ear, which is a vertex v whose polygon-interior angle is "
            "strictly convex (positive signed turn under an exact, tolerance-free orientation test; "
            "collinear triples are allowed as vertices but never as ears) and whose diagonal between "
            "its two neighbours lies fully inside the polygon with no other vertex in the resulting "
            "triangle. Among all valid ears, cut the one whose tip vertex appears earliest in the "
            "current vertex order. Record the tip's ORIGINAL index and the added diagonal's two "
            "ORIGINAL endpoint indices, with the two endpoints written in ascending order. Repeat "
            "until exactly three vertices remain.\n\n"
            "Answer exactly in the format  tips=[...] diags=[(a,c),(a,c),...]  : the ordered "
            "ear-tip original indices as tips, and the ordered diagonals you added as diags."
        )

    def score_answer(self, answer, entry):
        reference = str(entry["answer"]).strip()
        a = str(answer).strip()
        return 1.0 if a == reference else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'ear_clipping_triangulation (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dependence_relevance_r1/ear_clipping_triangulation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
