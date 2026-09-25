"""Track tetrahedral handedness through composed single ligand exchanges.

A molecule is drawn as a vertical chain of Fischer-projection stereocenters. Each
center carries four ranked substituents (CIP priority ranks 1<2<3<4) on the four
positions top/bottom/left/right; vertical bonds point away from the viewer and
horizontal bonds toward the viewer. A single exchange of any two ligands on a
center inverts that center's configuration (R <-> S). The instance applies a
sequence of single swaps that may target any center and asks for the final
configuration (R or S) of one queried center.
"""

import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

POSITIONS = ("top", "bottom", "left", "right")

# Right-handed embedding: +x east, +y north, +z toward the viewer.
# Fischer: vertical bonds (top/bottom) point away (-z), horizontal (left/right)
# point toward the viewer (+z).
_VEC = {
    "top": (0.0, 1.0, -1.0),
    "bottom": (0.0, -1.0, -1.0),
    "left": (-1.0, 0.0, 1.0),
    "right": (1.0, 0.0, 1.0),
}


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _norm(a):
    m = (a[0] * a[0] + a[1] * a[1] + a[2] * a[2]) ** 0.5
    return (a[0] / m, a[1] / m, a[2] / m)


def _rot_align(a, t):
    """Proper (det +1) rotation mapping unit vector a onto unit vector t."""
    # Rodrigues rotation about axis = cross(a, t).
    axis = _cross(a, t)
    la = (_dot(axis, axis)) ** 0.5
    if la < 1e-9:
        # a parallel or antiparallel to t.
        if _dot(a, t) > 0:
            return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        # 180 deg about any perpendicular axis.
        perp = _cross(a, (1.0, 0, 0)) if abs(a[0]) < 0.9 else _cross(a, (0.0, 1, 0))
        v = _norm(perp)
        vv = v
        return [
            [2 * vv[0] * vv[0] - 1, 2 * vv[0] * vv[1], 2 * vv[0] * vv[2]],
            [2 * vv[1] * vv[0], 2 * vv[1] * vv[1] - 1, 2 * vv[1] * vv[2]],
            [2 * vv[2] * vv[0], 2 * vv[2] * vv[1], 2 * vv[2] * vv[2] - 1],
        ]
    v = (axis[0] / la, axis[1] / la, axis[2] / la)
    K = [
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0],
    ]
    th = _dot(a, t)
    th = 1.0 if th > 1 else (-1.0 if th < -1 else th)
    th = math.acos(th)
    s, c = math.sin(th), math.cos(th)
    Kt = [[K[i][0] * c for i in range(3)] for _ in range(3)]
    # I + sin*K + (1-cos)*K^2
    K2 = [[sum(K[i][k] * K[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return [
        [(1 if i == j else 0) + s * K[i][j] + (1 - c) * K2[i][j] for j in range(3)]
        for i in range(3)
    ]


def _mm(M, v):
    return (
        M[0][0] * v[0] + M[0][1] * v[1] + M[0][2] * v[2],
        M[1][0] * v[0] + M[1][1] * v[1] + M[1][2] * v[2],
        M[2][0] * v[0] + M[2][1] * v[1] + M[2][2] * v[2],
    )


def _signum(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)


def _center_config(pos2rank):
    """Return 'R' or 'S' for a center given {position: rank} for ranks 1..4.

    Robust: rotate (det+1) so the lowest-priority group points away from the
    viewer, project the remaining three onto the viewing plane and read the
    cyclic orientation. R <-> signed area -1, S <-> +1 (validated against
    (R)-glyceraldehyde and the universal single-swap inversion law).
    """
    positions = {pos2rank[p]: p for p in POSITIONS}
    d4 = _VEC[positions[4]]
    R = _rot_align(_norm(d4), (0.0, 0.0, -1.0))
    proj = []
    for rk in (1, 2, 3):
        dd = _mm(R, _VEC[positions[rk]])
        proj.append((dd[0], dd[1]))
    area = (
        proj[0][0] * proj[1][1] - proj[0][1] * proj[1][0]
        + proj[1][0] * proj[2][1] - proj[1][1] * proj[2][0]
        + proj[2][0] * proj[0][1] - proj[2][1] * proj[0][0]
    )
    return "S" if _signum(area) > 0 else "R"


def _apply_parity(config, target_swaps):
    """Return the final 'R'/'S' of a center after target_swaps single exchanges."""
    base = _center_config(config)
    if target_swaps % 2:
        return "S" if base == "R" else "R"
    return base


@dataclass
class StereoParityConfig(Config):
    max_centers: int = 2
    max_swaps: int = 3

    def apply_difficulty(self, level):
        self.max_centers = 2 + level
        self.max_swaps = 2 * (level + 1) + 1


class StereoParityTransport(Task):
    summary = (
        "Track tetrahedral handedness through composed single ligand exchanges on "
        "Fischer sterocenters (vertical chain, horizontal ligands); a single swap "
        "inverts a center and distractor swaps on other centers leave it unchanged; "
        "return the queried center's final R or S."
    )
    design_choice = (
        "Represent stereocenters in Fischer projections with vertical chain and "
        "horizontal ligands; answer as R/S after a sequence of single swaps."
    )
    config_cls = StereoParityConfig

    def generate_entry(self):
        n_centers = random.randint(2, self.config.max_centers)
        centers = []
        for i in range(1, n_centers + 1):
            ranks = [1, 2, 3, 4]
            random.shuffle(ranks)
            positions = {p: ranks[k] for k, p in enumerate(POSITIONS)}
            centers.append({"id": f"C{i}", "positions": positions})
        query = random.choice(centers)
        n_swaps = random.randint(1, self.config.max_swaps)
        swaps = []
        for _ in range(n_swaps):
            c = random.choice(centers)
            a, b = random.sample(POSITIONS, 2)
            swaps.append([c["id"], a, b])
        # The queried center's final parity only depends on swaps that target it.
        target_swaps = sum(1 for s in swaps if s[0] == query["id"])
        answer = _apply_parity(query["positions"], target_swaps)
        return Entry(
            metadata={
                "centers": centers,
                "swaps": swaps,
                "query": query["id"],
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        lines = []
        lines.append(
            "Answer format: reply with exactly one letter, R or S. "
            "The molecule below is a vertical chain of stereocenters drawn as "
            "Fischer projections. Each center carries four substituents ranked by "
            "CIP priority 1 < 2 < 3 < 4 on four positions. In a Fischer projection "
            "the vertical (top/bottom) bonds point away from the viewer and the "
            "horizontal (left/right) bonds point toward the viewer."
        )
        for c in metadata["centers"]:
            pos = c["positions"]
            lines.append(f"{c['id']}: top {pos['top']}, bottom {pos['bottom']}, "
                         f"left {pos['left']}, right {pos['right']}")
        lines.append("The molecule now undergoes the following single ligand "
                     "exchanges, in order; each one swaps the substituents at two "
                     "named positions of a named center, and a single exchange on a "
                     "center inverts that center's configuration (R becomes S and "
                     "vice versa):")
        for i, (cid, a, b) in enumerate(metadata["swaps"], 1):
            lines.append(f"{i}. swap {a} and {b} on {cid}")
        lines.append(f"What letter, R or S, is the final configuration of "
                     f"{metadata['query']}?")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        ref = entry["answer"]
        a = str(answer).strip().upper()
        r = str(ref).strip().upper()
        return 1.0 if a == r else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'stereochemical_parity_transport (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_reusable_operations_r4/stereochemical_parity_transport',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
