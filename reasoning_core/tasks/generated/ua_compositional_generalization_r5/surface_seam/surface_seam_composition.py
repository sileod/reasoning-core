import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'surface_seam_composition (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r5/surface_seam_composition',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def boundary_components(faces, glue):
    """faces: list of list of edge-label-ids per face, listed in cyclic order.
    The i-th edge of a face lies between corner i and corner (i+1)%k.
    glue: dict mapping (fid, eid) -> (fid, eid, orient); each label appears on
    exactly two edges which are paired.

    Returns the number of boundary components of the cellular-glued surface,
    computed by half-edge tracing with DSU over identified corners.
    """
    # Assign a global corner id to each (face, corner_index).
    corner_id = {}
    corners = []
    for f in range(len(faces)):
        for idx in range(len(faces[f])):
            corner_id[(f, idx)] = len(corners)
            corners.append((f, idx))

    n = len(corners)
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1

    # Twin map for half-edges. A half-edge (f, i) is the directed edge leaving
    # corner (f, i) toward corner (f, i+1) within face f.
    twin = {}
    for (fa, ea) in glue:
        fb, eb, orient = glue[(fa, ea)]
        ka = len(faces[fa])
        kb = len(faces[fb])
        # preserve: corner (fa,ea)~(fb,eb) and (fa,ea+1)~(fb,eb+1)
        # reverse : corner (fa,ea)~(fb,eb+1) and (fa,ea+1)~(fb,eb)
        if orient == 1:
            union(corner_id[(fa, ea)], corner_id[(fb, eb)])
            union(corner_id[(fa, (ea + 1) % ka)], corner_id[(fb, (eb + 1) % kb)])
        else:
            union(corner_id[(fa, ea)], corner_id[(fb, (eb + 1) % kb)])
            union(corner_id[(fa, (ea + 1) % ka)], corner_id[(fb, eb)])
        if (fa, ea) not in twin:
            twin[(fa, ea)] = (fb, eb)
            twin[(fb, eb)] = (fa, ea)

    # Boundary components: build a graph on the distinct (identified) corner
    # classes that touch an unglued ("boundary") edge, with edges being the
    # boundary edges. Every boundary vertex has degree 2, so each connected
    # component is one closed loop = one boundary component.
    bparent = {}

    def bfind(x):
        while bparent[x] != x:
            bparent[x] = bparent[bparent[x]]
            x = bparent[x]
        return x

    def badd(x):
        if x not in bparent:
            bparent[x] = x

    for f in range(len(faces)):
        k = len(faces[f])
        for i in range(k):
            if (f, i) not in twin:
                ca = find(corner_id[(f, i)])
                cb = find(corner_id[(f, (i + 1) % k)])
                badd(ca)
                badd(cb)
                ra, rb = bfind(ca), bfind(cb)
                if ra != rb:
                    bparent[ra] = rb

    roots = set()
    for x in bparent:
        roots.add(bfind(x))
    return len(roots)


def generate_structure(level, rng):
    """Create faces and a glue mapping. Not every edge is glued: a random
    portion of edges are glued pairwise (each glued label appears on exactly
    two edges), the rest are left as boundary arcs of the resulting surface.
    Self-seams (two edges of the same face) and orientation twists are
    possible.

    Returns (faces, glue, onglue) where faces[f] is a list of label ids in
    cyclic order, glue maps (f, eid) -> (f, eid, orient) for glued edges, and
    onglue maps a glued (f, eid) to its label id (unpaired edges map to their
    own unique id).
    """
    nfaces = 3 + level
    while True:
        face_sizes = [rng.randint(3, 5) for _ in range(nfaces)]
        total = sum(face_sizes)
        if total >= 8:
            break

    edge_list = []  # (fid, eid)
    eid_counter = 0
    faces = []
    for f in range(len(face_sizes)):
        k = face_sizes[f]
        face = []
        for e in range(k):
            face.append(eid_counter)
            edge_list.append((f, e))
            eid_counter += 1
        faces.append(face)

    # Choose how many edge-pairs to glue. Leave some edges unglued so
    # boundary components vary while still producing real seams. Glue a
    # variable fraction so the boundary count spreads across a wide range.
    npairs_total = len(edge_list) // 2
    lo = 0.15
    hi = 1.0
    frac = lo + rng.random() * (hi - lo)
    n_glue_pairs = max(0, int(npairs_total * frac))
    n_glue_pairs = min(npairs_total, n_glue_pairs)

    rng.shuffle(edge_list)
    glued_set = set()
    glue = {}
    onglue = {}
    for i in range(n_glue_pairs):
        (fa, ea) = edge_list[2 * i]
        (fb, eb) = edge_list[2 * i + 1]
        orient = rng.choice([1, -1])
        glue[(fa, ea)] = (fb, eb, orient)
        glue[(fb, eb)] = (fa, ea, orient)
        glued_set.add((fa, ea))
        glued_set.add((fb, eb))

    # label ids: assign glued-pair labels and unglued-edge labels from a
    # randomly permuted pool spanning the full range, so labels of separated
    # values mix with boundary counts rather than mirroring them.
    total = len(edge_list)
    perm = list(range(total))
    rng.shuffle(perm)
    label_id = {}
    onglue = {}
    lid = 0
    for i in range(n_glue_pairs):
        (fa, ea) = edge_list[2 * i]
        (fb, eb) = edge_list[2 * i + 1]
        label_id[(fa, ea)] = perm[i]
        label_id[(fb, eb)] = perm[i]
        onglue[(fa, ea)] = perm[i]
        onglue[(fb, eb)] = perm[i]
    idx = n_glue_pairs
    for (f, e) in edge_list:
        if (f, e) in glued_set:
            continue
        label_id[(f, e)] = perm[idx]
        onglue[(f, e)] = perm[idx]
        idx += 1

    return faces, glue, onglue


def _to_prompt(faces, glue, onglue):
    nf = len(faces)
    faces_prompt = []
    for f in range(nf):
        names = [f"e{onglue[(f, e)]}" for e in range(len(faces[f]))]
        faces_prompt.append(names)

    seams = []
    glued_items = [(fa, ea) for (fa, ea) in glue]
    for (fa, ea) in glued_items:
        fb, eb, orient = glue[(fa, ea)]
        if (fa, ea) > (fb, eb):
            continue
        la = onglue[(fa, ea)]
        dir_txt = "the same direction" if orient == 1 else "the reverse direction"
        seams.append((la, f"edge e{la} of face {fa} is sewn, in {dir_txt}, "
                      f"to face {fb}'s edge e{onglue[(fb, eb)]}"))
    # Print the seam with the largest label last, so the prompt's final number
    # is a large edge label far above any boundary count.
    seams.sort(key=lambda t: t[0])
    seams = [t[1] for t in seams]

    lines = ["A flat polygon is cut out for each face."]
    for f in range(nf):
        lines.append(f"Face {f} has edges in cyclic order "
                     f"{', '.join(faces_prompt[f])}, with its listed edges "
                     f"shot clockwise around the face.")
    lines.append("Now the polygon edges are sewn together. Any edge not "
                 "mentioned below is left open and becomes part of the surface "
                 "boundary. The sewing rules are:")
    for s in seams:
        lines.append("  " + s + ".")
    lines.append("How many distinct boundary components (closed loops of "
                 "unsewn edges) does the resulting glued surface have? Answer "
                 "with a single non-negative integer.")
    return "\n".join(lines), faces_prompt, seams


@dataclass
class SeamConfig(Config):
    level_cap: int = 6

    def apply_difficulty(self, level):
        self.level_cap = level


class SurfaceSeamV1(Task):
    task_name = "surface_seam"
    summary = ("Sew labeled boundary arcs of polygonal surfaces with preserving "
               "or reversing orientation, including twists and self-seams; "
               "return boundary count, orientability, or Euler characteristic "
               "of a component.")
    design_choice = ("Instances give a list of polygonal faces with labeled "
                     "edges; solver returns the number of boundary components "
                     "of the glued surface.")
    config_cls = SeamConfig

    def generate_entry(self):
        level = self.config.level_cap
        faces, glue, onglue = generate_structure(level, random)
        ans = boundary_components(faces, glue)
        prompt, faces_prompt, seams = _to_prompt(faces, glue, onglue)
        data = {
            "prompt": prompt,
            "faces": faces_prompt,
            "seams": seams,
            "level": level,
            "answer": str(ans),
        }
        return Entry(metadata=data, answer=str(ans))

    def render_prompt(self, metadata):
        return metadata["prompt"]

    def score_answer(self, answer, entry):
        s = answer.strip()
        try:
            if int(s) == int(entry.answer):
                return 1.0
        except (ValueError, TypeError):
            return 0.0
        return 0.0
