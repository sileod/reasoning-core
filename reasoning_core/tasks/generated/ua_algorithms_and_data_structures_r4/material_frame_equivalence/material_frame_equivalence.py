import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'material_frame_equivalence (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_algorithms_and_data_structures_r4/material_frame_equivalence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

MAT = {
    "id": ((1, 0), (0, 1)),
    "r90": ((0, -1), (1, 0)),
    "r180": ((-1, 0), (0, -1)),
    "r270": ((0, 1), (-1, 0)),
    "m_x": ((1, 0), (0, -1)),
    "m_y": ((-1, 0), (0, 1)),
    "d": ((0, 1), (1, 0)),
    "a": ((0, -1), (-1, 0)),
}
SYMBOLS = list(MAT)


def _mm(A, B):
    return tuple(
        tuple(A[i][0] * B[0][j] + A[i][1] * B[1][j] for j in range(2))
        for i in range(2)
    )


def _mv(M, v):
    return (M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1])


def _compose(seq):
    M = ((1, 0), (0, 1))
    for s in seq:
        M = _mm(MAT[s], M)
    return M


def _symbol_of(M):
    for s in SYMBOLS:
        if MAT[s] == M:
            return s
    raise RuntimeError("linear map is not in the dihedral group")


def _inv(M):
    return ((M[0][0], M[1][0]), (M[0][1], M[1][1]))


def _factor(M, k):
    if k == 1:
        return [_symbol_of(M)]
    seq = [random.choice(SYMBOLS) for _ in range(k - 1)]
    P = _compose(seq)
    last = _mm(M, _inv(P))
    seq.append(_symbol_of(last))
    return seq


@dataclass
class MaterialFrameEquivalenceConfig(Config):
    n_points: int = 3
    chain_len: int = 2
    coord: int = 1

    def apply_difficulty(self, level):
        self.n_points = 3 + level
        self.chain_len = 2 + level
        self.coord = 1 + (level + 1) // 2


class MaterialFrameEquivalence(Task):
    summary = ("Compare two composed deformation chains of D4 rotations/reflections (with "
               "translations as velocity-inert distractors) acting on named velocities of a fixed "
               "set of material points; decide whether both produce the identical velocity field at "
               "every point, as balanced yes/no answers.")
    design_choice = ("Use a fixed set of material points with named velocities; ask whether two "
                     "composed deformation chains yield identical velocity fields at all points.")
    config_cls = MaterialFrameEquivalenceConfig
    task_version = 2

    def _new_velocity(self, coord):
        while True:
            v = (random.randint(-coord, coord), random.randint(-coord, coord))
            if v != (0, 0):
                return v

    @staticmethod
    def _with_translations(rot_seq, coord):
        out = []
        for s in rot_seq:
            if random.random() < 0.5:
                dx, dy = random.randint(-coord, coord), random.randint(-coord, coord)
                out.append(("T", (dx, dy)))
            out.append(("R", s))
        return out

    def generate_entry(self):
        n_points = self.config.n_points
        chain_len = self.config.chain_len
        coord = self.config.coord
        for _ in range(200):
            yes_target = random.random() < 0.5
            MB_sym = random.choice(SYMBOLS)
            MB = MAT[MB_sym]
            B_rot = _factor(MB, chain_len)
            velocities = [self._new_velocity(coord) for _ in range(n_points)]

            if yes_target:
                A_rot = _factor(MB, chain_len)
            else:
                found = None
                candidates = [s for s in SYMBOLS if s != MB_sym]
                random.shuffle(candidates)
                for cand in candidates:
                    Mc = MAT[cand]
                    if any(_mv(Mc, v) != _mv(MB, v) for v in velocities):
                        found = cand
                        break
                if found is None:
                    continue
                A_rot = _factor(MAT[found], chain_len)

            MA = _compose(A_rot)
            MBc = _compose(B_rot)
            same = all(_mv(MA, v) == _mv(MBc, v) for v in velocities)
            assert same == yes_target, "generated label must equal the actual field comparison"

            names = ["O%d" % (i + 1) for i in range(n_points)]
            points = [(names[i], (int(v[0]), int(v[1]))) for i, v in enumerate(velocities)]
            chainA = self._with_translations(A_rot, coord)
            chainB = self._with_translations(B_rot, coord)
            answer = "Yes" if same else "No"
            return Entry(metadata={
                "points": points,
                "chainA": chainA,
                "chainB": chainB,
                "rotA": A_rot,
                "rotB": B_rot,
                "same": same,
            }, answer=answer)
        raise RuntimeError("MaterialFrameEquivalence failed to construct an instance")

    @staticmethod
    def _render_chain(tokens):
        rendered = []
        for kind, value in tokens:
            if kind == "T":
                rendered.append("T(%d,%d)" % value)
            else:
                rendered.append(value)
        return rendered

    def render_prompt(self, metadata):
        lines = [
            "The material points below move with constant velocities. A linear map applied to a "
            "velocity vector rotates or reflects it, while a translation T(dx,dy) only shifts an "
            "object's position and leaves its velocity unchanged.",
            "Points:",
        ]
        for name, vel in metadata["points"]:
            lines.append("  %s has velocity %s." % (name, tuple(vel)))
        lines.append("Chain A applies the following maps in order:")
        lines.append("  " + " \u00b7 ".join(self._render_chain(metadata["chainA"])))
        lines.append("Chain B applies the following maps in order:")
        lines.append("  " + " \u00b7 ".join(self._render_chain(metadata["chainB"])))
        lines.append("Here r90/r180/r270 rotate counterclockwise by 90/180/270 degrees and m_x, m_y, "
                     "d, a reflect across the x-axis, y-axis, line y=x and line y=-x respectively.")
        lines.append("Do chains A and B produce the identical velocity field at all material points? "
                     "Answer exactly 'Yes' or 'No'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        ref = str(entry["answer"]).strip().lower()
        if ref not in ("yes", "no"):
            return 0.0
        a = str(answer).strip().lower()
        return 1.0 if a == ref else 0.0
