"""Winding region repair: update region classifications after a single vertex
edit (move/insert/delete) of an oriented closed path.

Each instance describes one oriented closed polygonal path and a single edit that
turns it into a second path. The crossing structure (planar arrangement) changes
only locally, so most region winding labels are unchanged. The task asks for the
compact list of (region_id, new_label) pairs whose winding label actually changes
because of the edit.

The canonical answer is the sorted list of changed (region_id, new_label) pairs,
sorted by region_id, with labels being integers (the winding number signed by the
orientation of the path). Only the changed regions are returned.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'winding_region_repair (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r5/winding_region_repair',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class WindingRegionRepairConfig(Config):
    n_vertices: int = 7
    n_edits: int = 1
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level
        base = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 10, 6: 11}.get(level, 7 + level)
        self.n_vertices = base if level > 0 else 5


def _signed_area(points):
    area = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return area / 2.0


def gen_seg_intersection(p11, p12, p21, p22):
    """Return intersection point of segments p11-p12 and p21-p22 or None."""
    x1, y1 = p11
    x2, y2 = p12
    x3, y3 = p21
    x4, y4 = p22
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-9:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def _collect_intersections(points):
    """Collect all edge-intersection points for the polyline polygon."""
    pts = list(points)
    n = len(pts)
    cross = []
    for i in range(n):
        a1 = pts[i]
        a2 = pts[(i + 1) % n]
        for j in range(i + 1, n):
            if (i == j) or ((i + 1) % n == j) or ((j + 1) % n == i):
                continue
            b1 = pts[j]
            b2 = pts[(j + 1) % n]
            ip = gen_seg_intersection(a1, a2, b1, b2)
            if ip is not None:
                cross.append(ip)
    return cross


def _winding_at(segments, query):
    """Winding number of closed polygon (segments) at query point by ray casting."""
    x, y = query
    wn = 0
    for (x1, y1), (x2, y2) in segments:
        if y1 <= y:
            if y2 > y:
                vx = x1 + (y - y1) / (y2 - y1) * (x2 - x1)
                if vx > x:
                    wn += 1
        else:
            if y2 <= y:
                vx = x1 + (y - y1) / (y2 - y1) * (x2 - x1)
                if vx > x:
                    wn -= 1
    return wn


def _arrangement_regions(points):
    """Decompose the plane arrangement induced by the polygon into faces with
    winding labels and region ids. Returns dict region_id -> label and a list of
    (point, region_id).
    """
    pts = list(points)
    n = len(pts)
    segments = [(pts[i], pts[(i + 1) % n]) for i in range(n)]

    cross = _collect_intersections(pts)

    xs = [p[0] for p in pts] + [c[0] for c in cross]
    ys = [p[1] for p in pts] + [c[1] for c in cross]

    # Sample representative points for each candidate region. We create a fine
    # grid of sampling points and cluster those sharing the same winding label
    # and connected component via the arrangement. To keep it tractable, we
    # sample a bounding box grid and assign each sample a winding label, then
    # group samples sharing identical (label, adjacent labels) into regions.
    xmin = min(xs) - 1.0
    xmax = max(xs) + 1.0
    ymin = min(ys) - 1.0
    ymax = max(ys) + 1.0

    grid = 24
    samples = []
    for i in range(grid):
        for j in range(grid):
            sx = xmin + (xmax - xmin) * (i + 0.5) / grid
            sy = ymin + (ymax - ymin) * (j + 0.5) / grid
            # skip samples on edges
            on_edge = False
            for (x1, y1), (x2, y2) in segments:
                if abs((x2 - x1) * (sy - y1) - (y2 - y1) * (sx - x1)) < 1e-6:
                    if min(x1, x2) - 1e-6 <= sx <= max(x1, x2) + 1e-6 and \
                       min(y1, y2) - 1e-6 <= sy <= max(y1, y2) + 1e-6:
                        on_edge = True
                        break
            if on_edge:
                continue
            wn = _winding_at(segments, (sx, sy))
            samples.append(((sx, sy), wn))

    # Group cells into regions: two cells are in the same region if they share a
    # boundary not crossed by an edge. We union sample cells that are orthogonally
    # adjacent AND have the same winding number AND no polygon edge separates them.
    parent = {}
    def init(k):
        parent.setdefault(k, k)
    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    cell_index = {}
    for idx, (pt, wn) in enumerate(samples):
        cell_index[idx] = (pt, wn)
        init(idx)

    step = (xmax - xmin) / grid
    for idx, (pt, wn) in enumerate(samples):
        sx, sy = pt
        # right neighbor
        rx = sx + step
        for target in ((rx, sy), (sx, sy + step)):
            matched = None
            for jdx, (q, wn2) in enumerate(samples):
                if abs(q[0] - target[0]) < 1e-9 and abs(q[1] - target[1]) < 1e-9:
                    matched = jdx
                    break
            if matched is None:
                continue
            _, wn2 = samples[matched]
            if wn2 == wn:
                # check no edge between the two cell centres
                blocked = False
                for (x1, y1), (x2, y2) in segments:
                    if gen_seg_intersection((sx, sy), target, (x1, y1), (x2, y2)) is not None:
                        blocked = True
                        break
                if not blocked:
                    union(idx, matched)

    # region id per cell
    comps = {}
    labels = {}
    for idx, (pt, wn) in enumerate(samples):
        r = find(idx)
        comps.setdefault(r, []).append(idx)
        labels[r] = wn

    # assign region ids deterministically
    region_ids = sorted(comps.keys(), key=lambda r: (labels[r], min(cell_index[i] for i in comps[r]), r))
    idmap = {r: i for i, r in enumerate(region_ids)}

    # representative point per region: the cell closest to the region centroid
    regions = {}
    rpoints = {}
    for r, idxs in comps.items():
        cnt = len(idxs)
        cx = sum(cell_index[i][0][0] for i in idxs) / cnt
        cy = sum(cell_index[i][0][1] for i in idxs) / cnt
        rep = None
        best = None
        for i in idxs:
            pt, wn = cell_index[i]
            d = (pt[0] - cx) ** 2 + (pt[1] - cy) ** 2
            if best is None or d < best:
                best = d
                rep = pt
        regions[idmap[r]] = labels[r]
        rpoints[idmap[r]] = rep
    return regions, rpoints


def _apply_move(points, i, dx, dy):
    new = [list(p) for p in points]
    nx, ny = new[i]
    new[i] = [nx + dx, ny + dy]
    return [tuple(p) for p in new]


def _apply_delete(points, i):
    new = [p for k, p in enumerate(points) if k != i]
    return new


def _apply_insert(points, i, pt):
    new = [list(p) for p in points]
    new.insert(i, list(pt))
    return [tuple(p) for p in new]


def _segments_of(points):
    pts = list(points)
    n = len(pts)
    return [(pts[i], pts[(i + 1) % n]) for i in range(n)]


def _changed_pairs(before_points, after_points):
    """Return sorted list of (new_region_id, new_label) pairs of regions whose
    winding label differs before/after the single vertex edit.

    A region in the after-arrangement is deemed 'changed' if the winding number
    at its representative point differs between the edited path and the original
    path evaluated at that same point. This localizes to exactly those regions
    whose classification the edit actually alters. Region ids are the ids of the
    after-arrangement; new_label is the after path's winding number there.
    """
    after, rpoints = _arrangement_regions(after_points)
    before_segs = _segments_of(before_points)
    after_segs = _segments_of(after_points)
    changes = []
    for rid in sorted(after.keys()):
        rep = rpoints[rid]
        wb = _winding_at(before_segs, rep)
        wa = _winding_at(after_segs, rep)
        if wb != wa:
            changes.append((rid, wa))
    changes.sort()
    return changes


class WindingRegionRepair(Task):
    """Update probe classifications after moving, inserting, or deleting vertices
    of oriented closed paths; handle self-crossings, nested loops, and boundary
    hits, returning only changed winding labels."""

    summary = ("Update probe classifications after moving, inserting, or deleting "
               "vertices of oriented closed paths; handle self-crossings, nested "
               "loops, and boundary hits, returning only changed winding labels.")
    design_choice = ("Each instance specifies a single edit (move/insert/delete) and "
                     "lists only the affected region labels, with answer as a compact "
                     "list of (region_id, new_label) pairs.")
    config_cls = WindingRegionRepairConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_vertices
        while True:
            pts = []
            for _ in range(n):
                pts.append((random.uniform(-5, 5), random.uniform(-5, 5)))
            # ensure the polygon is closed loop (n >= 4 for non-degenerate area)
            if _signed_area(pts) == 0:
                continue
            edit = random.choice(["move", "insert", "delete"])
            try:
                if edit == "move":
                    i = random.randrange(n)
                    dx = random.uniform(-2, 2)
                    dy = random.uniform(-2, 2)
                    after = _apply_move(pts, i, dx, dy)
                elif edit == "insert":
                    i = random.randrange(n + 1)
                    pt = (random.uniform(-5, 5), random.uniform(-5, 5))
                    after = _apply_insert(pts, i, pt)
                else:
                    i = random.randrange(n)
                    after = _apply_delete(pts, i)
                if len(after) < 4:
                    raise ValueError
                if _signed_area(after) == 0:
                    raise ValueError
                changes = _changed_pairs(pts, after)
                if not changes:
                    raise ValueError
                ans = ";".join(f"{rid}:{lab}" for rid, lab in changes)
                metadata = {
                    "before_vertices": pts,
                    "after_vertices": after,
                    "edit": edit,
                    "edit_index": i,
                    "changed_pairs": changes,
                    "answer": ans,
                }
                assert isinstance(ans, str)
                return Entry(metadata=metadata, answer=ans)
            except (ValueError, ZeroDivisionError):
                continue

    def render_prompt(self, metadata):
        pts = metadata["before_vertices"]
        after = metadata["after_vertices"]
        edit = metadata["edit"]
        i = metadata["edit_index"]
        before_str = ";".join(f"{x:g},{y:g}" for x, y in pts)
        after_str = ";".join(f"{x:g},{y:g}" for x, y in after)
        if edit == "move":
            edit_desc = f"vertex index {i} is moved (the others stay fixed)"
        elif edit == "insert":
            edit_desc = f"a new vertex is inserted at index {i}"
        else:
            edit_desc = f"the vertex at index {i} is deleted"
        return (
            f"An oriented closed polygonal path with vertices "
            f"(x,y) = [{before_str}] has winding regions. Give each closed "
            f"region a unique integer id by its winding number around the path. "
            f"Then the path is edited: {edit_desc}, making the new vertex list "
            f"[{after_str}]. Recompute the winding regions of the new path. "
            f"List, as 'region_id:new_label' pairs separated by ';', ONLY the "
            f"regions whose winding label changed due to this single edit, "
            f"sorted by region_id. Region ids and labels are integers. "
            f"Do not list regions whose label stayed the same."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = entry.metadata.get("answer")
        if gold is None:
            gold = entry.answer
        if answer.strip() == gold:
            return 1.0
        # robust: allow whitespace / trailing semicolon tolerance
        def norm(s):
            return ";".join(p.strip() for p in s.strip().strip(";").split(";") if p.strip())
        return 1.0 if norm(answer) == norm(gold) else 0.0
