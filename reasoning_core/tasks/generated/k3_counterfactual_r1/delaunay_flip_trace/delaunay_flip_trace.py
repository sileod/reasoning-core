import random
from dataclasses import dataclass

import numpy as np
from scipy.spatial import Delaunay

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'delaunay_flip_trace (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/delaunay_flip_trace',
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


def _orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _in_circle(a, b, c, d):
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d
    adx, ady = ax - dx, ay - dy
    bdx, bdy = bx - dx, by - dy
    cdx, cdy = cx - dx, cy - dy
    a2 = adx * adx + ady * ady
    b2 = bdx * bdx + bdy * bdy
    c2 = cdx * cdx + cdy * cdy
    return (adx * (bdy * c2 - b2 * cdy) - ady * (bdx * c2 - b2 * cdx)
            + a2 * (bdx * cdy - bdy * cdx))


def _locally_illegal(pts, a, b, apexx, apexy):
    return _orient(pts[a], pts[b], pts[apexx]) * _in_circle(pts[a], pts[b], pts[apexx], pts[apexy]) > 0


def _edge_list(tris):
    edges = set()
    for t in tris:
        a, b, c = sorted(t)
        edges.update(((a, b), (a, c), (b, c)))
    return sorted(edges)


def _flip_pair(tri_set, edge):
    shared = [t for t in tri_set if all(v in t for v in edge)]
    if len(shared) != 2:
        return None
    t1, t2 = shared
    sh = tuple(sorted(set(t1) & set(t2)))
    a1 = (set(t1) - set(sh)).pop()
    a2 = (set(t2) - set(sh)).pop()
    return t1, t2, sh, a1, a2


def _run_flips(pts, tri_set, maxsteps=300):
    tri_set = {tuple(sorted(t)) for t in tri_set if len(t) == 3}
    flip_trace = []
    for _ in range(maxsteps):
        failing = None
        for e in _edge_list(tri_set):
            pair = [t for t in tri_set if all(v in t for v in e)]
            if len(pair) != 2:
                continue
            sh = tuple(sorted(set(pair[0]) & set(pair[1])))
            a1 = (set(pair[0]) - set(sh)).pop()
            a2 = (set(pair[1]) - set(sh)).pop()
            if _locally_illegal(pts, sh[0], sh[1], a1, a2):
                if failing is None or sh < failing:
                    failing = sh
        if failing is None:
            return flip_trace, frozenset(tri_set)
        r = _flip_pair(tri_set, failing)
        if r is None:
            return flip_trace, frozenset(tri_set)
        t1, t2, sh, a1, a2 = r
        tri_set.discard(t1)
        tri_set.discard(t2)
        tri_set.add(tuple(sorted((a1, a2, sh[0]))))
        tri_set.add(tuple(sorted((a1, a2, sh[1]))))
        flip_trace.append(failing)
    return flip_trace, frozenset(tri_set)


def _cocircular(pts, a, b, c, d):
    xa, ya = pts[a]
    xb, yb = pts[b]
    xc, yc = pts[c]
    xd, yd = pts[d]
    return _in_circle((xa, ya), (xb, yb), (xc, yc), (xd, yd)) == 0


def _general_position(pts):
    n = len(pts)
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                if _orient(pts[a], pts[b], pts[c]) == 0:
                    return False
    for a in range(n):
        for b in range(a + 1, n):
            for c in range(b + 1, n):
                for d in range(c + 1, n):
                    if _cocircular(pts, a, b, c, d):
                        return False
    return True


@dataclass
class DelaunayFlipConfig(Config):
    point_count: int = 6
    disturb: int = 2

    def apply_difficulty(self, level):
        self.point_count = min(5 + level, 11)
        self.disturb = 2 + level


class DelaunayFlipTrace(Task):
    summary = ("Test the edges of a given triangulation of points in general "
               "position with the exact in-circle predicate, always flipping the "
               "smallest failing edge; return the flip sequence or the final "
               "Delaunay edge set.")
    config_cls = DelaunayFlipConfig
    design_choice = ("Return the flip sequence as a list of edge indices (i,j) in "
                     "the order flipped, using the exact in-circle predicate with "
                     "arbitrary-precision arithmetic.")

    def generate_entry(self):
        n = self.config.point_count
        disturb = self.config.disturb
        for _ in range(5000):
            pts = []
            while len(pts) < n:
                p = (random.randint(-40, 40), random.randint(-40, 40))
                if p not in pts:
                    pts.append(p)
            if not _general_position(pts):
                continue
            arr = np.array(pts, dtype=float)
            try:
                tri = Delaunay(arr)
            except Exception:
                continue
            tset = set(tuple(sorted(int(x) for x in s)) for s in tri.simplices)
            if len(tset) < 2:
                continue
            dist = set(tset)
            for _ in range(disturb):
                candidates = []
                for e in _edge_list(dist):
                    r = _flip_pair(dist, e)
                    if r is not None:
                        candidates.append(r)
                if not candidates:
                    break
                t1, t2, sh, a1, a2 = candidates[random.randrange(len(candidates))]
                dist.discard(t1)
                dist.discard(t2)
                dist.add(tuple(sorted((a1, a2, sh[0]))))
                dist.add(tuple(sorted((a1, a2, sh[1]))))
            flips, _final = _run_flips(pts, dist)
            if not flips:
                continue
            start_edges = _edge_list(dist)
            answer = ",".join(f"({i},{j})" for (i, j) in _sorted_flips(flips))
            metadata = {
                "points": pts,
                "start_edges": start_edges,
                "flip_sequence": [tuple(sorted(e)) for e in flips],
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not generate delaunay flip instance")

    def render_prompt(self, metadata):
        pts = metadata["points"]
        pts_repr = ", ".join(f"({p[0]},{p[1]})" for p in pts)
        edges = metadata["start_edges"]
        edges_repr = ", ".join(f"({i},{j})" for (i, j) in edges)
        return (f"We have points P = {{{pts_repr}}}, indexed 0 to {len(pts) - 1} "
                f"in the order listed, in general position (no three collinear, no "
                f"four cocircular). A triangulation of P is fully specified by its "
                f"edge set E = {{{edges_repr}}}. Apply the Delaunay flip algorithm: "
                f"repeatedly test each interior edge (an edge shared by two "
                f"triangles) with the exact in-circle predicate; an edge is "
                f"non-Delaunay when the vertex opposite one incident triangle lies "
                f"strictly inside the circumcircle of the other. Always flip the "
                f"single lexicographically smallest failing edge in that step "
                f"(compare first endpoint, then second). Stop when no interior "
                f"edge fails. Report the flip sequence as a comma-separated list "
                f"of flipped edges (i,j), each with endpoints in increasing order, "
                f"in the exact order flipped, e.g. (1,3),(0,2). Answer with only "
                f"the flip sequence.")

    def score_answer(self, answer, entry):
        expected = entry.metadata["flip_sequence"]
        expected_str = ",".join(f"({i},{j})" for (i, j) in expected)
        if answer is None:
            return 0.0
        norm = "".join(answer.split())
        if norm == expected_str:
            return 1.0
        return 0.0


def _sorted_flips(flips):
    return [tuple(sorted((int(i), int(j)))) for (i, j) in flips]
