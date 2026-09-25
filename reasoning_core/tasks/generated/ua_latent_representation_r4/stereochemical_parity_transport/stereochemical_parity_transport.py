import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

POSITIONS = ["T", "R", "B", "L"]

LIGAND_POOL = ["OH", "NH2", "CH3", "H", "Cl", "Br", "F", "OMe"]


def _arrangement_parity(seq):
    """Parity (0=even,1=odd) of the permutation given by the position sequence. The
    reference is the canonical ordering of the distinct ligands sorted lexicographically."""
    order = {lig: i for i, lig in enumerate(sorted(seq))}
    idx = [order[x] for x in seq]
    inv = 0
    for i in range(len(idx)):
        for j in range(i + 1, len(idx)):
            if idx[i] > idx[j]:
                inv += 1
    return inv % 2


def _op_sign(op):
    typ = op["type"]
    if typ == "swap":
        return -1
    if typ == "rotate90":
        return -1
    if typ == "cycle":
        return 1
    raise RuntimeError("unknown op")


def _apply_op(arr, op):
    typ = op["type"]
    if typ == "swap":
        a, b = op["a"], op["b"]
        arr[a], arr[b] = arr[b], arr[a]
    elif typ == "cycle":
        a, b, c = op["a"], op["b"], op["c"]
        arr[a], arr[b], arr[c] = arr[c], arr[a], arr[b]
    elif typ == "rotate90":
        # out-of-plane rotation: 4-cycle T<-R<-B<-L (odd permutation)
        t, r, b, l = arr["T"], arr["R"], arr["B"], arr["L"]
        arr["T"] = b
        arr["R"] = t
        arr["B"] = l
        arr["L"] = r
    return arr


@dataclass
class StereochemicalParityConfig(Config):
    min_ops: int = 1
    max_ops: int = 2

    def apply_difficulty(self, level):
        self.min_ops = 1 + level
        self.max_ops = 4 + 2 * level


class StereochemicalParityTransport(Task):
    summary = ("Track D/L handedness of a tetrahedral stereocenter in a Fischer projection "
               "through mixed single-exchanges, 3-cycles, and 90-degree out-of-plane rotations; "
               "return the queried center's final D or L configuration.")
    design_choice = ("Represent the initial stereocenter as a Fischer projection and query the "
                     "final parity after a series of ligand exchanges plus a 90-degree "
                     "out-of-plane rotation, with answer as D or L.")
    config_cls = StereochemicalParityConfig
    task_version = 2

    def generate_entry(self):
        while True:
            ligands = random.sample(LIGAND_POOL, 4)
            probe = ligands[0]
            others = ligands[1:]

            # Initial Fischer drawing: probe on a horizontal bond (R or L)
            probe_side = random.choice(["R", "L"])
            horiz = random.choice(["T", "B"])
            arr = {"T": None, "R": None, "B": None, "L": None}
            arr[probe_side] = probe
            rest = others[:]
            random.shuffle(rest)
            arr[horiz] = rest[0]
            vert1 = next(p for p in POSITIONS if arr[p] is None)
            arr[vert1] = rest[1]
            vert2 = next(p for p in POSITIONS if arr[p] is None)
            arr[vert2] = rest[2]

            initial_label = "D" if probe_side == "R" else "L"

            n_ops = random.randint(self.config.min_ops, self.config.max_ops)
            ops = []
            for _ in range(n_ops):
                typ = random.choice(["swap", "swap", "cycle", "rotate90"])
                if typ == "swap":
                    a, b = random.sample(POSITIONS, 2)
                    ops.append({"type": "swap", "a": a, "b": b})
                elif typ == "cycle":
                    a, b, c = random.sample(POSITIONS, 3)
                    ops.append({"type": "cycle", "a": a, "b": b, "c": c})
                else:
                    ops.append({"type": "rotate90"})

            init_parity = _arrangement_parity([arr[p] for p in POSITIONS])
            working = dict(arr)
            op_sign = 1
            for op in ops:
                op_sign *= _op_sign(op)
                _apply_op(working, op)

            final_parity = _arrangement_parity([working[p] for p in POSITIONS])
            assert (init_parity ^ final_parity) == ((1 - op_sign) // 2) % 2, \
                "transport inconsistency"

            final_label = ("D" if initial_label == "D" else "L") if op_sign == 1 else (
                "L" if initial_label == "D" else "D")
            assert final_label in ("D", "L")

            return Entry(
                metadata={
                    "ligands": ligands,
                    "arrangement": arr,
                    "initial_label": initial_label,
                    "ops": ops,
                    "op_sign": op_sign,
                    "final_label": final_label,
                    "cot": "initial=" + initial_label + " ops=" + repr(ops),
                },
                answer=final_label,
            )

    def render_prompt(self, metadata):
        arr = metadata["arrangement"]
        lines = [
            "A stereocenter is drawn as a Fischer projection. In a Fischer projection the "
            "vertical bonds (T top, B bottom) point away from the viewer and the horizontal "
            "bonds (R right, L left) point toward the viewer.",
            "",
            f"The probe group is {metadata['ligands'][0]}. The center is D-configured when the "
            "probe lies on the RIGHT horizontal bond and L-configured when it lies on the LEFT "
            "horizontal bond.",
            "",
            "Initial drawing - top, right, bottom, left: "
            f"({arr['T']}, {arr['R']}, {arr['B']}, {arr['L']}). "
            f"The initial configuration is {metadata['initial_label']}.",
            "",
            "The following operations are then applied in order:",
        ]
        for op in metadata["ops"]:
            if op["type"] == "swap":
                lines.append(f"  - exchange the single substituents at positions {op['a']} and {op['b']}")
            elif op["type"] == "cycle":
                lines.append(
                    f"  - cyclically rotate the substituents at positions {op['a']}, {op['b']}, {op['c']}")
            else:
                lines.append("  - rotate the fragment 90 degrees out of the plane")
        lines += [
            "",
            "Rules: exchanging two single substituents flips D<->L; a 3-cycle of three "
            "substituents leaves D/L unchanged; a 90-degree out-of-plane rotation flips D<->L.",
            "",
            "What is the final configuration of the center? Reply using just one letter.",
        ]
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if answer is None:
            return 0.0
        a = str(answer).strip().upper()
        if a == "D" or a == "L":
            return 1.0 if a == gold else 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'stereochemical_parity_transport (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_representation_r4/stereochemical_parity_transport',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
