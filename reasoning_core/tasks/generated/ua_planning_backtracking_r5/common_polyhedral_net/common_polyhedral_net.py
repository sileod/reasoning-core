import math
import random
from collections import deque, defaultdict
from dataclasses import dataclass
from itertools import combinations

from reasoning_core.template import Config, Entry, Task

_OPP = {(0, 1), (2, 3), (4, 5)}


def _octa_edges():
    return [(i, j) for i in range(6) for j in range(i + 1, 6) if (i, j) not in _OPP]


_OCTA = _octa_edges()


def _is_tree(edges):
    if len(edges) != 5:
        return False
    parent = list(range(6))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    cnt = 0
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            cnt += 1
    return cnt == 5


_TREES = []
for _combo in combinations(range(12), 5):
    _ed = [tuple(sorted(_OCTA[i])) for i in _combo]
    if _is_tree(_ed):
        _TREES.append(tuple(sorted(_ed)))

_FACE_NAMES = {0: "top", 1: "bottom", 2: "front", 3: "back", 4: "left", 5: "right"}


def _corners(dims):
    W, H, D = dims
    return {
        0: [(0, 0, D), (W, 0, D), (W, H, D), (0, H, D)],
        1: [(0, 0, 0), (W, 0, 0), (W, H, 0), (0, H, 0)],
        2: [(0, 0, 0), (W, 0, 0), (W, 0, D), (0, 0, D)],
        3: [(0, H, 0), (W, H, 0), (W, H, D), (0, H, D)],
        4: [(0, 0, 0), (0, H, 0), (0, H, D), (0, 0, D)],
        5: [(W, 0, 0), (W, H, 0), (W, H, D), (W, 0, D)],
    }


def _strict_overlap(r1, r2):
    return r1[0] < r2[2] and r2[0] < r1[2] and r1[1] < r2[3] and r2[1] < r1[3]


def valid_net(dims, tree):
    W, H, D = dims
    corners = _corners(dims)
    flat = {}
    c = corners[0]
    base = [(0, 0), (W, 0), (W, H), (0, H)]
    flat[0] = {c[i]: base[i] for i in range(4)}
    adj = defaultdict(list)
    for a, b in tree:
        adj[a].append(b)
        adj[b].append(a)
    visited = {0}
    dq = deque([0])
    while dq:
        f = dq.popleft()
        for g in adj[f]:
            if g in visited:
                continue
            visited.add(g)
            shared = [pt for pt in corners[f] if pt in corners[g]]
            if len(shared) != 2:
                return False
            A, B = shared[0], shared[1]
            p1 = flat[f][A]
            p2 = flat[f][B]
            xs = [flat[f][pt][0] for pt in corners[f]]
            ys = [flat[f][pt][1] for pt in corners[f]]
            cx = sum(xs) / 4.0
            cy = sum(ys) / 4.0
            mx = (p1[0] + p2[0]) / 2.0
            my = (p1[1] + p2[1]) / 2.0
            edx = p2[0] - p1[0]
            edy = p2[1] - p1[1]
            perp = (0, 1)
            for nx, ny in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                if nx * edx + ny * edy != 0:
                    continue
                inward = nx * (cx - mx) + ny * (cy - my)
                if inward < 0:
                    perp = (nx, ny)
                    break
            nx, ny = perp
            other = [pt for pt in corners[g] if pt not in shared]
            P = other[0]
            Ax, Ay, Az = A
            Bx, By, Bz = B
            Px, Py, Pz = P
            vx, vy, vz = Bx - Ax, By - Ay, Bz - Az
            wx, wy, wz = Px - Ax, Py - Ay, Pz - Az
            crmag = math.hypot(
                wy * vz - wz * vy, wz * vx - wx * vz, wx * vy - wy * vx
            )
            abmag = math.hypot(vx, vy, vz)
            breadth = int(round(crmag / abmag)) if abmag else 1
            pos_g = {A: p1, B: p2}
            for Ppt in other:
                da = math.dist(Ppt, A)
                db = math.dist(Ppt, B)
                basept = p1 if da <= db else p2
                pos_g[Ppt] = (basept[0] + nx * breadth, basept[1] + ny * breadth)
            flat[g] = pos_g
            dq.append(g)
    if len(visited) != 6:
        return False
    rects = []
    for f, mp in flat.items():
        xs = [v[0] for v in mp.values()]
        ys = [v[1] for v in mp.values()]
        rects.append((min(xs), min(ys), max(xs), max(ys)))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if _strict_overlap(rects[i], rects[j]):
                return False
    return True


_CYCLE = [(0, 2), (0, 4), (2, 4)]


@dataclass
class PolyNetConfig(Config):
    num_polyhedra: int = 1
    dim_hi: int = 2
    max_forced: int = 0

    def apply_difficulty(self, level):
        self.num_polyhedra = 2 + level // 2
        self.dim_hi = 2 + level // 2
        self.max_forced = level


class CommonPolyhedralNet(Task):
    summary = (
        "Find edge cuts whose unfolded faces form one nonoverlapping planar net for each of "
        "several supplied polyhedra; respect forbidden seams and face correspondences, returning "
        "a shared net or impossibility."
    )
    config_cls = PolyNetConfig
    task_version = 2

    def _any_dims(self):
        return tuple(random.randint(1, self.config.dim_hi) for _ in range(3))

    def _valid_dims_for(self, tree):
        for _ in range(200):
            dims = self._any_dims()
            if valid_net(dims, tree):
                return dims
        raise RuntimeError("no valid dims found for tree")

    def generate_entry(self):
        K = self.config.num_polyhedra
        possible = random.random() < 0.5
        specs = []
        if possible:
            dims1 = self._any_dims()
            valid = [t for t in _TREES if valid_net(dims1, t)]
            tree = random.choice(valid)
            for i in range(K):
                dims = dims1 if i == 0 else self._valid_dims_for(tree)
                nf = random.randint(0, min(self.config.max_forced, len(tree)))
                flist = random.sample(list(tree), nf)
                random.shuffle(flist)
                cut = random.randint(0, len(flist))
                seams = flist[:cut]
                corr = flist[cut:]
                specs.append((dims, seams, corr))
            for dims, seams, corr in specs:
                if not valid_net(dims, tree):
                    raise RuntimeError("gold net not valid for spec")
                for e in seams + corr:
                    if e not in tree:
                        raise RuntimeError("forced edge outside tree")
            answer = "yes"
            meta_tree = sorted(tree)
        else:
            meta_tree = None
            for i in range(K):
                dims = self._any_dims()
                if i == 0:
                    flist = list(_CYCLE)
                else:
                    nf = random.randint(0, self.config.max_forced)
                    flist = random.sample(_OCTA, min(nf, len(_OCTA)))
                random.shuffle(flist)
                cut = random.randint(0, len(flist))
                seams = flist[:cut]
                corr = flist[cut:]
                specs.append((dims, seams, corr))
            answer = "no"
        meta = {
            "possible": possible,
            "answer": answer,
            "specs": specs,
            "tree": meta_tree,
        }
        return Entry(metadata=meta, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        for idx, (dims, seams, corr) in enumerate(metadata["specs"]):
            name = chr(ord("A") + idx)
            seam_s = ", ".join("%d-%d" % (a, b) for a, b in sorted(seams)) or "none"
            corr_s = ", ".join("%d-%d" % (a, b) for a, b in sorted(corr)) or "none"
            deploy = "x".join(str(x) for x in dims)
            lines.append(
                "Box %s: %s cuboid. Must-join seams (forbidden to cut): %s. "
                "Face-correspondence pairs (must be directly joined): %s."
                % (name, deploy, seam_s, corr_s)
            )
        body = "\n".join(lines)
        prefix = (
            "Label the 6 faces of every box: 0 top, 1 bottom, 2 front, 3 back, 4 left, 5 right. "
            "A planar net of a box is its 6 faces unfolded flat into a single connected, "
            "non-overlapping piece by keeping some edges joined (hinged seams) and cutting the "
            "rest. You have several boxes; each lists face pairs that must stay joined in the "
            "net: 'must-join seams' (edges forbidden to cut) and 'face-correspondence pairs' "
            "(face pairs that must be directly joined as a seam). Decide whether a single common "
            "hinged-edge set is a valid planar net for every box while including all of its "
            "required joints."
        )
        q = (
            "Does one common net exist that is a valid planar net for every box and includes "
            "every required joint? Answer 'yes' if such a shared net exists and 'no' if it "
            "does not."
        )
        return prefix + "\n" + body + "\n" + q

    def score_answer(self, answer, entry):
        meta = entry.metadata
        if meta["possible"]:
            return 1.0 if answer.strip() == "yes" else 0.0
        return 1.0 if answer.strip() == "no" else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'common_polyhedral_net (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_planning_backtracking_r5/common_polyhedral_net',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
