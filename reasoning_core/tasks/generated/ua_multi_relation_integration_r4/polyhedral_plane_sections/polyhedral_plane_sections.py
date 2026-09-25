import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

import numpy as np


TASK_META = {'parent_source_id': None,
 'idea': 'polyhedral_plane_sections (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_multi_relation_integration_r4/polyhedral_plane_sections',
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


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def _gen_prism(n, base_scale, h):
    pts = []
    for i in range(n):
        ang = 2 * np.pi * i / n + random.uniform(-0.2, 0.2)
        r = base_scale * (1 + random.uniform(-0.2, 0.2))
        pts.append((r * np.cos(ang), r * np.sin(ang), 0.0))
    for (x, y, _) in list(pts):
        pts.append((x, y, h))
    faces = [list(range(n)), list(range(n, 2 * n))]
    for i in range(n):
        faces.append([i, (i + 1) % n, n + (i + 1) % n, n + i])
    return pts, faces


def _gen_pyramid(n, base_scale, h):
    pts = []
    for i in range(n):
        ang = 2 * np.pi * i / n + random.uniform(-0.2, 0.2)
        r = base_scale * (1 + random.uniform(-0.2, 0.2))
        pts.append((r * np.cos(ang), r * np.sin(ang), 0.0))
    pts.append((random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), h))
    faces = [list(range(n))]
    for i in range(n):
        faces.append([i, (i + 1) % n, n])
    return pts, faces


def _edges_from_faces(faces):
    edges = set()
    for f in faces:
        m = len(f)
        for i in range(m):
            a, b = f[i], f[(i + 1) % m]
            edges.add((min(a, b), max(a, b)))
    return list(edges)


def _centroid(pts):
    return np.mean(np.array(pts, dtype=float), axis=0)


def _sect_vertices(n, d, pts, edges):
    pts_a = np.array(pts, dtype=float)
    found = set()
    for (i, j) in edges:
        a = pts_a[i]
        b = pts_a[j]
        denom = float(np.dot(n, b - a))
        if abs(denom) < 1e-9:
            continue
        t = (d - float(np.dot(n, a))) / denom
        if -1e-7 <= t <= 1 + 1e-7:
            p = a + t * (b - a)
            found.add(tuple(np.round(p, 6)))
    return found


def _span(pts):
    pts_a = np.array(pts, dtype=float)
    mn = pts_a.min(axis=0)
    mx = pts_a.max(axis=0)
    return float(np.linalg.norm(mx - mn))


def _build_solid(config):
    kind = random.random()
    if kind < 0.4:
        k = "prism"
        n = random.choice([3, 4, 5, 6])
        pts, faces = _gen_prism(n, config.base_scale, config.height)
    elif kind < 0.75:
        k = "pyramid"
        n = random.choice([3, 4, 5])
        pts, faces = _gen_pyramid(n, config.base_scale, config.height)
    else:
        k = "beveled"
        if random.random() < 0.5:
            n = random.choice([3, 4, 5, 6])
            pts, faces = _gen_prism(n, config.base_scale, config.height)
        else:
            n = random.choice([3, 4, 5])
            pts, faces = _gen_pyramid(n, config.base_scale, config.height)
    edges = _edges_from_faces(faces)
    return k, pts, edges


def _gen_cut(k, pts, edges, config):
    pts_a = np.array(pts, dtype=float)
    centroid = _centroid(pts)
    mode = random.choice(["oblique", "vertex", "edge"])

    if mode == "oblique":
        a = random.uniform(0.4, 2.5)
        b = random.uniform(0.4, 2.5)
        c = random.uniform(0.4, 2.5)
        n = _unit(np.array([a, b, c], dtype=float))
        base_d = float(np.dot(n, centroid))
        for _ in range(300):
            off = random.uniform(0.05, 1.0) * (1 if random.random() < 0.5 else -1)
            d = base_d + off
            nv = len(_sect_vertices(n, d, pts, edges))
            if nv >= 3:
                return n, d, mode, nv
        d = base_d
        nv = len(_sect_vertices(n, d, pts, edges))
        if nv >= 3:
            return n, d, mode, nv
        raise RuntimeError("no oblique section")
    elif mode == "vertex":
        a = random.uniform(0.4, 2.5)
        b = random.uniform(0.4, 2.5)
        c = random.uniform(0.4, 2.5)
        n = _unit(np.array([a, b, c], dtype=float))
        for _ in range(300):
            v = np.array(random.choice(pts_a), dtype=float)
            d = float(np.dot(n, v))
            nv = len(_sect_vertices(n, d, pts, edges))
            if nv >= 3:
                return n, d, mode, nv
        raise RuntimeError("no vertex section")
    else:
        # plane through an edge (two adjacent vertices)
        a = random.uniform(0.4, 2.5)
        b = random.uniform(0.4, 2.5)
        c = random.uniform(0.4, 2.5)
        n0 = _unit(np.array([a, b, c], dtype=float))
        for _ in range(300):
            i, j = random.choice(edges)
            vi = np.array(pts_a[i], dtype=float)
            vj = np.array(pts_a[j], dtype=float)
            e = vj - vi
            if abs(float(np.dot(n0, e))) < 1e-6:
                continue
            vv = np.cross(e, n0)
            nn = _unit(vv - np.dot(vv, n0) * n0 if False else vv)
            d = float(np.dot(nn, vi))
            if abs(float(np.dot(nn, vj)) - d) > 1e-3:
                continue
            nv = len(_sect_vertices(nn, d, pts, edges))
            if nv >= 3:
                return nn, d, mode, nv
        raise RuntimeError("no edge section")


@dataclass
class PlaneSectionsConfig(Config):
    base_scale: float = 2.0
    height: float = 3.0

    def apply_difficulty(self, level):
        self.base_scale = 2.0 + 0.6 * level
        self.height = 2.5 + 0.6 * level


class PolyhedralPlaneSections(Task):
    summary = "Intersect specified planes with prisms, pyramids, and beveled solids, including oblique cuts and cuts through vertices or edges; return the section's vertex count or boundary labels."
    config_cls = PlaneSectionsConfig

    def generate_entry(self):
        for _try in range(50):
            k, pts, edges = _build_solid(self.config)
            try:
                n, d, mode, nv = _gen_cut(k, pts, edges, self.config)
            except RuntimeError:
                continue
            config_meta = {
                "solid": k,
                "mode": mode,
                "normal": (round(float(n[0]), 4), round(float(n[1]), 4), round(float(n[2]), 4)),
                "const": round(float(d), 4),
                "n_vertices": int(nv),
            }
            return Entry(
                metadata=config_meta,
                answer=str(int(nv)),
            )
        raise RuntimeError("could not generate a valid section")

    def render_prompt(self, metadata):
        s = metadata["solid"]
        mode = metadata["mode"]
        nx, ny, nz = metadata["normal"]
        d = metadata["const"]
        shapes = {"prism": "a right prism",
                  "pyramid": "a pyramid",
                  "beveled": "a beveled polyhedron"}
        cut_desc = {
            "oblique": "an oblique plane",
            "vertex": "a plane passing through a vertex of the solid",
            "edge": "a plane passing through an edge of the solid",
        }[mode]
        return (f"A plane cuts {shapes[s]}. The plane is {cut_desc} and is given by "
                f"({nx:.3f}) x + ({ny:.3f}) y + ({nz:.3f}) z = {d:.3f}. "
                f"The section of the solid by this plane is a convex polygon. "
                f"How many vertices does the section have? The answer is a single integer.")

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(answer) == entry.metadata["n_vertices"] else 0.0
        except (ValueError, TypeError):
            return 0.0
