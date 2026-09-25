import random
from dataclasses import dataclass

import numpy as np

from reasoning_core.template import Config, Entry, Task


@dataclass
class CellSurgeryConfig(Config):
    side: int = 4
    max_components: int = 2
    max_holes: int = 1

    def apply_difficulty(self, level):
        self.side = 4 + level
        self.max_components = 1 + (level // 2) + (1 if level >= 5 else 0)
        self.max_holes = min(2 + level, (self.side * self.side) // 7 + 1)


def _gf2_rank(A):
    A = A.astype(np.uint8).copy()
    m, n = A.shape
    rank = 0
    for col in range(n):
        pivot = -1
        for r in range(rank, m):
            if A[r, col]:
                pivot = r
                break
        if pivot == -1:
            continue
        A[[rank, pivot]] = A[[pivot, rank]]
        for r in range(m):
            if r != rank and A[r, col]:
                A[r] ^= A[rank]
        rank += 1
        if rank == m:
            break
    return rank


def _components(occupied):
    vertices = set()
    edges = set()
    for (x, y) in occupied:
        c00, c10, c01, c11 = (x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)
        vertices.update([c00, c10, c01, c11])
        edges.add(frozenset((c00, c10)))
        edges.add(frozenset((c01, c11)))
        edges.add(frozenset((c00, c01)))
        edges.add(frozenset((c10, c11)))
    parent = {v: v for v in vertices}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for e in edges:
        a, b = tuple(e)
        union(a, b)
    return len({find(v) for v in vertices})


def _homology(occupied):
    cells = sorted(occupied)
    verts = set()
    edges = set()
    for (x, y) in cells:
        c00, c10, c01, c11 = (x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)
        verts.update([c00, c10, c01, c11])
        edges.add(frozenset((c00, c10)))
        edges.add(frozenset((c01, c11)))
        edges.add(frozenset((c00, c01)))
        edges.add(frozenset((c10, c11)))
    nV, nE, nF = len(verts), len(edges), len(cells)
    vid = {v: i for i, v in enumerate(sorted(verts))}
    eid = {e: i for i, e in enumerate(sorted(edges, key=sorted))}
    d1 = np.zeros((nE, nV), dtype=np.uint8)
    for e, i in eid.items():
        a, b = tuple(sorted(e))
        d1[i, vid[a]] = 1
        d1[i, vid[b]] = 1
    d2 = np.zeros((nF, nE), dtype=np.uint8)
    for fi, (x, y) in enumerate(cells):
        c00, c10, c01, c11 = (x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)
        for e in (frozenset((c00, c10)), frozenset((c01, c11)),
                  frozenset((c00, c01)), frozenset((c10, c11))):
            d2[fi, eid[e]] = 1
    r1 = _gf2_rank(d1)
    r2 = _gf2_rank(d2)
    b0, b1, b2 = nV - r1, (nE - r1) - r2, nF - r2
    assert b2 == 0, (b2, occupied)
    assert b0 == _components(occupied), (b0, occupied)
    assert b0 >= 1 and b1 >= 0
    chi = nV - nE + nF
    assert chi == b0 - b1 + b2
    return int(b0), int(b1), int(b2)


def _build_complex(side, n_comp, n_holes):
    occupied = set()
    kinds = [False] * (n_comp - n_holes) + [True] * n_holes
    random.shuffle(kinds)
    for kind in kinds:
        placed = False
        for _ in range(80):
            if kind:
                if side < 3:
                    rx = ry = side
                else:
                    rx = random.randint(3, min(4, side))
                    ry = random.randint(3, min(4, side))
            else:
                rx = random.randint(1, min(3, side))
                ry = random.randint(1, min(3, side))
            x0 = random.randint(0, side - rx)
            y0 = random.randint(0, side - ry)
            cells = set()
            for dx in range(rx):
                for dy in range(ry):
                    if kind and 0 < dx < rx - 1 and 0 < dy < ry - 1:
                        continue
                    cells.add((x0 + dx, y0 + dy))
            if not cells:
                continue
            ok = True
            for (xx, yy) in cells:
                for nb in ((xx + 1, yy), (xx - 1, yy), (xx, yy + 1), (xx, yy - 1)):
                    if nb in occupied:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                occupied |= cells
                placed = True
                break
        if not placed:
            for _ in range(80):
                x0 = random.randint(0, side - 1)
                y0 = random.randint(0, side - 1)
                if (x0, y0) not in occupied and not any(
                        nb in occupied for nb in
                        ((x0 + 1, y0), (x0 - 1, y0), (x0, y0 + 1), (x0, y0 - 1))):
                    occupied.add((x0, y0))
                    placed = True
                    break
    if not occupied:
        occupied.add((random.randint(0, side - 1), random.randint(0, side - 1)))
    return occupied


def _render_grid(occupied, side):
    lines = []
    for y in range(side - 1, -1, -1):
        row = " ".join("*" if (x, y) in occupied else "." for x in range(side))
        lines.append(f"y={y}   {row}")
    lines.append("      " + " ".join(str(x) for x in range(side)))
    return "\n".join(lines)


def _intervention(occupied, side):
    op = random.choice(["excise", "add", "drill"])
    if op == "excise":
        cell = random.choice(sorted(occupied))
        text = (f"excise the cell at ({cell[0]},{cell[1]}), removing that unit of "
                f"material together with its boundary edges")
    elif op == "add":
        empty = set((x, y) for x in range(side) for y in range(side)) - set(occupied)
        if empty:
            cell = random.choice(sorted(empty))
            text = f"add a solid cell at ({cell[0]},{cell[1]}), filling that empty grid position"
        else:
            cell = random.choice(sorted(occupied))
            text = f"add supporting material around the cell at ({cell[0]},{cell[1]})"
    else:
        cell = random.choice(sorted(occupied))
        text = (f"drill a tunnel through the interior of the cell at "
                f"({cell[0]},{cell[1]})")
    return {"op": op, "cell": [int(cell[0]), int(cell[1])], "text": text}


class CellSurgeryHomology(Task):
    summary = ("Report pre-surgery (components, tunnels, cavities) homology of a 2D "
               "cubical complex of occupied grid cells with varied component and hole "
               "structure under a plain-language cell-surgery intervention context.")
    design_choice = ("Instances give a small cubical complex as a set of occupied grid cells; "
                     "the answer is a triple of integers (components, tunnels, cavities) for the "
                     "pre-intervention complex, with the intervention described in plain language.")
    config_cls = CellSurgeryConfig

    def generate_entry(self):
        side = self.config.side
        n_comp = random.randint(1, self.config.max_components)
        max_h = min(self.config.max_holes, n_comp)
        n_holes = random.randint(0, max_h)
        occupied = _build_complex(side, n_comp, n_holes)
        b0, b1, b2 = _homology(occupied)
        inter = _intervention(occupied, side)
        metadata = {
            "side": side,
            "occupied": [[x, y] for (x, y) in sorted(occupied)],
            "grid_text": _render_grid(occupied, side),
            "cells_str": ", ".join(f"{x},{y}" for (x, y) in sorted(occupied)),
            "intervention": inter,
            "intervention_text": inter["text"],
            "homology": [int(b0), int(b1), int(b2)],
        }
        return Entry(metadata=metadata, answer=f"{b0} {b1} {b2}")

    def render_prompt(self, metadata):
        return (
            "A cubical complex is given by its occupied unit cells (*) marked on the grid "
            "below. Coordinates are (x,y): x runs left to right, y runs bottom to top, and "
            "each row is labeled by its y value.\n\n"
            f"{metadata['grid_text']}\n\n"
            f"The occupied cells are: {{{metadata['cells_str']}}}.\n\n"
            f"A surgical procedure is planned: {metadata['intervention_text']}\n\n"
            "Compute the homology of the complex as it stands BEFORE any surgical change. "
            "Report the triple (components, tunnels, cavities) as three integers separated "
            "by single spaces, e.g. '2 1 0'."
        )

    def score_answer(self, answer, entry):
        gold = tuple(int(p) for p in entry.answer.split())
        if isinstance(answer, str):
            parts = answer.strip().split()
            if len(parts) == 3:
                try:
                    got = tuple(int(p) for p in parts)
                except ValueError:
                    return 0.0
                if got == gold:
                    return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'cell_surgery_homology (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/cell_surgery_homology',
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
