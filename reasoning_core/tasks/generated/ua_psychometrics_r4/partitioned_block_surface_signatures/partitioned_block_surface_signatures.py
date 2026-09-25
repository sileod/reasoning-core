import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'partitioned_block_surface_signatures (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_psychometrics_r4/partitioned_block_surface_signatures',
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

_bal_counter = 0


@dataclass
class PartitionedBlockConfig(Config):
    size: int = 3
    stages: int = 3

    def apply_difficulty(self, level):
        self.stages = 3 + level
        self.size = 3


class PartitionedBlockSurfaceSignatures(Task):
    summary = "Propagate face markings through paint, mask, cut, and repaint stages on blocks with uneven partitions; return the number of pieces bearing a requested combination of marked and cut faces."
    design_choice = "Vary the partition geometry: fixed 2x2 grid vs. irregular polyomino regions on a 3x3x3 block, changing which faces belong to which piece."
    config_cls = PartitionedBlockConfig
    task_version = 2

    COLORS = ["red", "blue", "green"]

    def _gen_partition(self, size):
        cells = [(x, y, z) for x in range(size) for y in range(size) for z in range(size)]
        nregions = random.randint(2, 3)
        order = list(cells)
        random.shuffle(order)
        part = {}
        for r in range(nregions):
            if r == nregions - 1:
                count = len(order)
            else:
                count = random.randint(1, len(order) - (nregions - 1 - r))
            for _ in range(count):
                part[order.pop(0)] = r
        regions = [sorted([c for c in cells if part[c] == r]) for r in range(nregions)]
        return nregions, regions

    def _build_piece_map(self, regions):
        cell2piece = {}
        for r, reg in enumerate(regions):
            for c in reg:
                cell2piece[c] = r
        return cell2piece

    def _exposed_faces(self, size, cell2piece):
        states = {}
        for cell in cell2piece:
            x, y, z = cell
            coords = [x, y, z]
            for a in range(3):
                if coords[a] == 0:
                    states[(a, 0, cell)] = {"color": None, "masked": False, "cut": False}
                if coords[a] == size - 1:
                    states[(a, 1, cell)] = {"color": None, "masked": False, "cut": False}
        return states

    def _gen_ops(self, stages):
        ops = []
        for _ in range(stages):
            kind = random.choice(["paint", "mask", "cut", "repaint"])
            if kind == "paint":
                ops.append(("paint", random.choice(self.COLORS)))
            elif kind == "mask":
                ops.append(("mask", random.randint(1, 4)))
            elif kind == "cut":
                ops.append(("cut", random.randint(0, 2)))
            else:
                ops.append(("repaint", random.choice(self.COLORS)))
        return ops

    def _apply(self, states, op, size, cell2piece):
        kind = op[0]
        if kind == "paint":
            color = op[1]
            for st in states.values():
                if not st["masked"]:
                    st["color"] = color
        elif kind == "repaint":
            color = op[1]
            for st in states.values():
                if st["color"] is None and not st["masked"]:
                    st["color"] = color
        elif kind == "mask":
            n = op[1]
            candidates = [k for k, st in states.items() if not st["masked"]]
            random.shuffle(candidates)
            for k in candidates[:n]:
                states[k]["masked"] = True
        elif kind == "cut":
            a = op[1]
            for key in list(states.keys()):
                axis, sign, cell = key
                if axis != a:
                    continue
                x, y, z = cell
                ncoord = [x, y, z]
                step = 1 if sign == 0 else -1
                ncoord[axis] += step
                nx, ny, nz = ncoord
                ncell = (nx, ny, nz)
                if (0 <= nx < size and 0 <= ny < size and 0 <= nz < size
                        and cell2piece.get(ncell) == cell2piece.get(cell)):
                    nkey = (axis, sign, ncell)
                    states[nkey] = {"color": None, "masked": False, "cut": True}
                    if nkey != key:
                        del states[key]
                else:
                    del states[key]

    def _gen_request(self):
        qcolor = random.choice(self.COLORS)
        combo = random.choice(["marked_only", "marked_and_cut"])
        n_mark = random.randint(1, 2)
        return {"color": qcolor, "combo": combo, "n_mark": n_mark}

    def _count_answer(self, states, nregions, cell2piece, req):
        color = req["color"]
        n_mark = req["n_mark"]
        marked = [0] * nregions
        cut_any = [False] * nregions
        for key, st in states.items():
            axis, sign, cell = key
            p = cell2piece.get(cell)
            if p is None:
                continue
            if st["color"] == color:
                marked[p] += 1
            if st["cut"]:
                cut_any[p] = True
        total = 0
        for r in range(nregions):
            if req["combo"] == "marked_only":
                if marked[r] >= n_mark:
                    total += 1
            else:
                if marked[r] >= n_mark and cut_any[r]:
                    total += 1
        return total

    def generate_entry(self):
        global _bal_counter
        size = self.config.size
        stages = self.config.stages
        target = _bal_counter % 3
        accepted = None
        for _ in range(400):
            nregions, regions = self._gen_partition(size)
            cell2piece = self._build_piece_map(regions)
            states = self._exposed_faces(size, cell2piece)
            ops = self._gen_ops(stages)
            for op in ops:
                self._apply(states, op, size, cell2piece)
            req = self._gen_request()
            answer = self._count_answer(states, nregions, cell2piece, req)
            if not (0 <= answer <= nregions):
                continue
            if answer == target:
                accepted = (nregions, regions, cell2piece, states, ops, req, answer)
                break
            accepted = (nregions, regions, cell2piece, states, ops, req, answer)
        _bal_counter += 1
        nregions, regions, cell2piece, states, ops, req, answer = accepted
        metadata = {
            "size": size,
            "regions": regions,
            "ops": ops,
            "req": req,
            "nregions": nregions,
        }
        return Entry(metadata=metadata, answer=str(answer))

    def render_prompt(self, metadata):
        size = metadata["size"]
        regions = metadata["regions"]
        ops = metadata["ops"]
        req = metadata["req"]
        reg_lines = [f"piece {i}: cells {reg}" for i, reg in enumerate(regions)]
        op_lines = []
        for op in ops:
            if op[0] == "paint":
                op_lines.append(f"paint every exposed unmasked face {op[1]}")
            elif op[0] == "repaint":
                op_lines.append(f"repaint {op[1]} onto every exposed face that is uncolored and unmasked")
            elif op[0] == "mask":
                op_lines.append(f"mask {op[1]} currently colorable exposed faces")
            else:
                op_lines.append(f"cut along axis {op[1] + 1}, peeling every piece one layer inward and exposing fresh uncolored unmarked faces")
        if req["combo"] == "marked_only":
            combo_txt = f"that are colored {req['color']}"
        else:
            combo_txt = f"that are colored {req['color']} and were exposed by a cut"
        return (
            f"A {size}x{size}x{size} block of unit cells is split into uneven pieces. "
            + "; ".join(reg_lines)
            + ". "
            + " ".join(op_lines)
            + f" Count how many pieces have at least {req['n_mark']} exposed faces {combo_txt}; "
            + f"answer with that single integer for this {size}x{size}x{size} block."
        )

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(str(answer).strip()) == int(entry.answer) else 0.0
        except Exception:
            return 0.0
