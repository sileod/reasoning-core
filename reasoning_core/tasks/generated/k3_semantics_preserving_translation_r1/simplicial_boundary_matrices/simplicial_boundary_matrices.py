import random
from itertools import combinations

from reasoning_core.template import Config, Entry, Task, Reward

TASK_META = {'parent_source_id': None,
 'idea': 'simplicial_boundary_matrices (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_semantics_preserving_translation_r1/simplicial_boundary_matrices',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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


design_choice = ("Answer as a canonical sparse matrix string listing only nonzero entries "
                 "with row,col:value pairs, ordered by row then column.")


def _sparse_string(gf2, nrow, ncol, entries):
    """entries: dict mapping (row,col)->value (or set of (row,col) for gf2).

    Returns canonical string of sorted row,col:value entries.
    """
    if gf2:
        items = sorted(entries)
    else:
        items = sorted(entries.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    if not items:
        return f"0x{nrow}x{ncol}"
    parts = []
    for it in items:
        if gf2:
            r, c = it
            parts.append(f"{r},{c}:1")
        else:
            (r, c), v = it
            parts.append(f"{r},{c}:{v}")
    return ";".join(parts)


class SimplicialConfig(Config):
    max_verts = 5

    def apply_difficulty(self, level):
        self.max_verts = 5 + level


class SimplicialBoundaryMatrices(Task):
    summary = ("Translate a simplicial complex to its GF(2) or signed boundary matrix across "
               "a queried dimension, or rebuild the complex from a given boundary matrix; "
               "answer a canonical sparse matrix string or a sorted simplex list.")
    config_cls = SimplicialConfig
    task_version = 2

    def _build_complex(self):
        """Return (nverts, faces_by_dim) where faces_by_dim[d] is the sorted list of
        d-simplices present (as sorted tuples of vertex indices). Closure holds:
        every face of a present simplex is present."""
        mv = self.config.max_verts
        nverts = random.randint(max(3, mv - 2), mv)
        verts = list(range(nverts))
        dim = random.randint(1, min(2, nverts - 1))

        # choose edges (1-simplices)
        all_edges = [tuple(sorted(c)) for c in combinations(verts, 2)]
        random.shuffle(all_edges)
        n_edges = random.randint(max(1, len(all_edges) // 3), len(all_edges))
        edges = set(all_edges[:n_edges])

        faces = {0: [tuple([v]) for v in verts], 1: sorted(edges)}
        for d in range(2, dim + 1):
            cur = []
            for c in combinations(verts, d + 1):
                c = tuple(sorted(c))
                if all(tuple(sorted(sub)) in faces[d - 1] for sub in combinations(c, d)):
                    if random.random() < 0.4:
                        cur.append(c)
            faces[d] = sorted(cur)
            # enforce closure: all faces of these are already in lower dims by check
        return nverts, faces

    def generate_entry(self):
        mode = getattr(self.config, "mode", None)
        if mode is None:
            mode = random.choice(["gf2", "signed", "reverse"])
        nverts, faces = self._build_complex()

        # determine max present dimension
        maxdim = max(d for d in faces if faces[d])

        if mode in ("gf2", "signed"):
            q = random.randint(0, maxdim - 1) if maxdim >= 1 else 0
            q = max(0, min(q, maxdim - 1))
            qfaces = faces.get(q, [])
            q1faces = faces.get(q + 1, []) if q + 1 in faces else []

            # order q+1 faces by (len, sorted) for column order
            # order q faces by (len, sorted) for row order
            def keyf(f):
                return (len(f), tuple(sorted(f)))
            qfaces_sorted = sorted(qfaces, key=keyf)
            q1_sorted = sorted(q1faces, key=keyf)
            row_index = {f: i for i, f in enumerate(qfaces_sorted)}
            col_index = {f: i for i, f in enumerate(q1_sorted)}

            gf2 = mode == "gf2"
            entries = {}
            for ci, face in enumerate(q1_sorted):
                for sub in combinations(face, q + 1):
                    sub = tuple(sorted(sub))
                    if sub in row_index:
                        r = row_index[sub]
                        if gf2:
                            entries[(r, ci)] = 1
                        else:
                            # signed incidence: sign = (-1)^(position of removed vertex)
                            verts_sorted = sorted(face)
                            # sub is face minus one vertex; find its position
                            missing = set(face) - set(sub)
                            missing_v = missing.pop()
                            pos = sorted(verts_sorted).index(missing_v)
                            val = (-1) ** pos
                            entries[(r, ci)] = val

            rowcol = (nverts, maxdim + 1)
            ans = _sparse_string(gf2, len(qfaces_sorted), len(q1_sorted), entries)
            metadata = {
                "mode": mode,
                "nverts": nverts,
                "faces": {str(d): [list(f) for f in faces[d]] for d in faces},
                "q": q,
                "row_simplices_order": [[int(x) for x in f] for f in qfaces_sorted],
                "col_simplices_order": [[int(x) for x in f] for f in q1_sorted],
                "nrow": len(qfaces_sorted),
                "ncol": len(q1_sorted),
                "gf2": gf2,
            }
            # Self-check: rebuild from ans equals entries
            assert _sparse_string(gf2, len(qfaces_sorted), len(q1_sorted), entries) == ans
            return Entry(metadata=metadata, answer=ans)

        else:
            # reverse: given a boundary matrix (rows = q-simplices, cols = (q+1)-simplices),
            # identify which vertices/q-simplices. Simpler: give the GF(2) matrix and ask
            # for the set of (q+1)-simplices (columns) that have a nonzero column, plus
            # expand: answer the complex's list of all simplices.
            # We'll rebuild the complex from a matrix: give the set of edges (1-simplices)
            # encoded by an adjacency-like incidence matrix and ask for the full complex
            # including triangles implied by edges.
            reverse_mode = random.choice(["closure"])
            # Build complex, give boundary_1 matrix (vertices x edges), ask for all edges
            # and the filled-in triangles -> answer the simplex list.
            nverts, faces = self._build_complex()
            verts = list(range(nverts))
            edges = faces[1]
            # answer: sorted list of all simplices (all dims) as sets
            all_simplices = []
            for d, fl in faces.items():
                for f in fl:
                    all_simplices.append(sorted(f))
            all_simplices_keyed = sorted(all_simplices, key=lambda s: (len(s), s))
            ans = ";".join(",".join(map(str, s)) for s in all_simplices_keyed)

            metadata = {
                "mode": mode,
                "nverts": nverts,
                "edges": [list(e) for e in edges],
            }
            return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        mode = metadata["mode"]
        if mode == "gf2":
            faces = metadata["faces"]
            lines = []
            for d in sorted(faces, key=int):
                lines.append(f"dimension {d}: " + ", ".join("{" + " ".join(map(str, f)) + "}" for f in faces[d]))
            return (f"A simplicial complex has vertices 0..{metadata['nverts']-1}. "
                    f"Its faces are:\n" + "\n".join(lines) +
                    f"\nCompute the boundary matrix over GF(2) between dimension "
                    f"{metadata['q']} and dimension {metadata['q']+1}. Rows are the "
                    f"dimension-{metadata['q']} simplices in this order: "
                    + ", ".join("{" + " ".join(map(str, f)) + "}" for f in metadata["row_simplices_order"]) +
                    f". Columns are the dimension-{metadata['q']+1} simplices in this order: "
                    + ", ".join("{" + " ".join(map(str, f)) + "}" for f in metadata["col_simplices_order"]) +
                    ". The matrix has " + str(metadata["nrow"]) + " rows and " +
                    str(metadata["ncol"]) + " columns (dimensions " + str(metadata["nrow"]) +
                    "x" + str(metadata["ncol"]) + "). Answer as a sparse matrix "
                    "row,col:1 pairs (all entries are 1 mod 2) separated by semicolons, "
                    "ordered by row then column. Use 0x{n}x{m} if the matrix is all zero.")
        if mode == "signed":
            faces = metadata["faces"]
            lines = []
            for d in sorted(faces, key=int):
                lines.append(f"dimension {d}: " + ", ".join("{" + " ".join(map(str, f)) + "}" for f in faces[d]))
            return (f"A simplicial complex has vertices 0..{metadata['nverts']-1}. "
                    f"Its faces are:\n" + "\n".join(lines) +
                    f"\nCompute the signed incidence boundary matrix between dimension "
                    f"{metadata['q']} and dimension {metadata['q']+1}. Rows are the "
                    f"dimension-{metadata['q']} simplices in this order: "
                    + ", ".join("{" + " ".join(map(str, f)) + "}" for f in metadata["row_simplices_order"]) +
                    f". Columns are the dimension-{metadata['q']+1} simplices in this order: "
                    + ", ".join("{" + " ".join(map(str, f)) + "}" for f in metadata["col_simplices_order"]) +
                    ". For each column simplex, write its vertices in increasing order; "
                    "the entry in the row whose simplex is that column with the vertex at "
                    "position i removed equals (-1)^i. The matrix has " +
                    str(metadata["nrow"]) + " rows and " + str(metadata["ncol"]) +
                    " columns. Answer as sparse row,col:value pairs with value -1 or 1, "
                    "separated by semicolons, ordered by row then column. Use 0x{n}x{m} "
                    "if the matrix is all zero.")
        # reverse
        edges = metadata["edges"]
        return (f"A simplicial complex on vertices 0..{metadata['nverts']-1} is known only "
                f"by its edges, which are:\n"
                + ", ".join("{" + " ".join(map(str, e)) + "}" for e in edges) +
                f".\nIt is closed under taking faces: whenever a k-simplex is present, "
                f"every (k-1)-face of it is present, and conversely any set of vertices "
                f"all of whose pairwise edges are present forms a simplex. Rebuild the "
                f"full complex and list every simplex as comma-separated vertex indices "
                f"{'{a},{b},{c}'} for {metadata['nverts']} vertices, ordered by dimension "
                f"then lexicographically within a dimension, joined by semicolons.")

    def score_answer(self, answer, entry):
        return answer == entry.answer
