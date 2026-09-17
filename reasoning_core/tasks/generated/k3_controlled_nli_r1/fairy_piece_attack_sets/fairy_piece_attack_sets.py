"""Fairy chess piece attack sets on an 8x8 board.

Generator places a stipulated fairy piece (leaper, rider, hopper, or locust)
together with blockers, screens and enemy pieces, then asks for the piece's
legal destinations (moves and captures) as a canonical sorted list.
"""

import random
from dataclasses import dataclass

TASK_META = {'parent_source_id': None,
 'idea': 'fairy_piece_attack_sets (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r1/fairy_piece_attack_sets',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

from reasoning_core.template import Config, Entry, Task

FILES = "abcdefgh"

LEAPERS = {
    "knight": [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)],
    "camel": [(1, 3), (3, 1), (-1, 3), (-3, 1), (1, -3), (3, -1), (-1, -3), (-3, -1)],
    "zebra": [(2, 3), (3, 2), (-2, 3), (-3, 2), (2, -3), (3, -2), (-2, -3), (-3, -2)],
    "alfil": [(1, 1), (1, -1), (-1, 1), (-1, -1)],
    "dabbaba": [(1, 0), (-1, 0), (0, 1), (0, -1)],
    "threeleaper": [(3, 0), (-3, 0), (0, 3), (0, -3)],
}
RIDER_DIRS = {
    "rook": [(1, 0), (-1, 0), (0, 1), (0, -1)],
    "bishop": [(1, 1), (1, -1), (-1, 1), (-1, -1)],
    "queen": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
    "nightrider": [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)],
    "camelrider": [(1, 3), (3, 1), (-1, 3), (-3, 1), (1, -3), (3, -1), (-1, -3), (-3, -1)],
}
HOPPER_DIRS = {
    "grasshopper": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
    "eq": [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)],
    "erebus_diag": [(1, 1), (1, -1), (-1, 1), (-1, -1)],
}
LOCUST_DIRS = {
    "locust": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
}
FAMILIES = (
    list(LEAPERS) + list(RIDER_DIRS) + list(HOPPER_DIRS) + list(LOCUST_DIRS)
)

PIECE_RULES = """Rules for fairy pieces:
- A leaper jumps by fixed offsets (e.g. a camel moves by 3+1) and is never blocked.
- A rider slides along rays (like rook/bishop) until it would leave the board; it stops
  before a friendly piece, or captures an enemy piece and stops there.
- A hopper moves along a ray exactly like a rider while traveling, but instead of
  stopping on the first piece, it must jump over exactly one piece (the screen) of
  either colour and land on the square immediately beyond it: that square must be
  empty, or hold an enemy piece which is captured. If there is no screen on a ray
  the hopper cannot move along that ray.
- A locust moves along a ray, captures by jumping over exactly one enemy piece
  (the first piece on the ray) and must land on the square immediately beyond it,
  which must be empty. A locust captures no other way and only captures; a ray
  whose first piece is absent or friendly gives no move."""


def sq_name(f, r):
    return f"{FILES[f]}{r + 1}"


def _moves_for(kind, name, pos, occ):
    """occ: dict (f, r) -> 'F' friendly / 'E' enemy. Returns set of destination squares."""
    f0, r0 = pos
    dests = set()

    def inside(f, r):
        return 0 <= f < 8 and 0 <= r < 8

    if kind == "leaper":
        for df, dr in LEAPERS[name]:
            f, r = f0 + df, r0 + dr
            if inside(f, r) and occ.get((f, r)) != "F":
                dests.add((f, r))
    elif kind == "rider":
        for df, dr in RIDER_DIRS[name]:
            f, r = f0 + df, r0 + dr
            while inside(f, r):
                o = occ.get((f, r))
                if o is None:
                    dests.add((f, r))
                elif o == "E":
                    dests.add((f, r))
                    break
                else:
                    break
                f, r = f + df, r + dr
    elif kind == "hopper":
        for df, dr in HOPPER_DIRS[name]:
            f, r = f0 + df, r0 + dr
            while inside(f, r) and (f, r) not in occ:
                f, r = f + df, r + dr
            if inside(f, r) and (f, r) in occ:
                f, r = f + df, r + dr
                if inside(f, r) and occ.get((f, r)) != "F":
                    dests.add((f, r))
    elif kind == "locust":
        for df, dr in LOCUST_DIRS[name]:
            f, r = f0 + df, r0 + dr
            if inside(f, r) and occ.get((f, r)) == "E":
                f, r = f + df, r + dr
                if inside(f, r) and (f, r) not in occ:
                    dests.add((f, r))
    return dests


def _classify(kind, name):
    if kind == "hopper":
        return "hopper"
    if kind == "locust":
        return "locust"
    return kind


@dataclass
class FairyAttackConfig(Config):
    n_occupants: int = 5
    enemy_ratio: float = 0.5

    def apply_difficulty(self, level):
        self.n_occupants = 3 + 3 * int(level)
        self.enemy_ratio = 0.5


class FairyPieceAttackSets(Task):
    summary = (
        "Project stipulated fairy-piece movement - leapers by offset vectors, riders "
        "until blocked, hoppers needing a screen, locust captures - onto an 8x8 board "
        "with friendly/enemy occupants, and list one piece's destinations as sorted "
        "algebraic squares."
    )
    config_cls = FairyAttackConfig
    task_version = 2

    def _build(self):
        kind = random.choice(["leaper", "rider", "hopper", "locust"])
        name = random.choice(
            list(LEAPERS if kind == "leaper" else
                 RIDER_DIRS if kind == "rider" else
                 HOPPER_DIRS if kind == "hopper" else LOCUST_DIRS)
        )
        n = self.config.n_occupants
        n = min(n, 63)
        squares = random.sample(range(64), n + 1)
        pos = (squares[0] % 8, squares[0] // 8)
        occ = {}
        for s in squares[1:]:
            sq = (s % 8, s // 8)
            occ[sq] = "E" if random.random() < self.config.enemy_ratio else "F"
        # ensure non-empty destination set; locust in particular needs enemies
        if not _moves_for(kind, name, pos, occ):
            return None
        return kind, name, pos, occ

    def generate_entry(self):
        for _ in range(200):
            built = self._build()
            if built is not None:
                kind, name, pos, occ = built
                break
        else:
            raise RuntimeError("fairy_piece_attack_sets: could not build instance")
        dests = _moves_for(kind, name, pos, occ)
        answer = ",".join(sq_name(f, r) for f, r in sorted(dests))
        if not answer or not all(dests):
            raise RuntimeError("fairy_piece_attack_sets: invalid instance")
        meta = {
            "piece": name,
            "family": _classify(kind, name),
            "position": sq_name(*pos),
            "occupants": {sq_name(f, r): c for (f, r), c in sorted(occ.items())},
        }
        return Entry(metadata=meta, answer=answer)

    def render_prompt(self, metadata):
        occ_txt = ", ".join(
            f"{sq} ({'friendly' if c == 'F' else 'enemy'})"
            for sq, c in metadata["occupants"].items()
        )
        fam = metadata["family"]
        piece = metadata["piece"]
        pos = metadata["position"]
        art = "an" if piece[0] in "aeiou" else "a"
        p = f"""On this otherwise empty 8x8 chessboard (files a-h, ranks 1-8), {art} {piece} ({fam}) stands on {pos}.
Other pieces on the board: {occ_txt if occ_txt else "none"}.

{PIECE_RULES}

List every square the {piece} can move to, including capture squares, as a comma-separated list of algebraic coordinates in ascending alphabetical order (file letter first, then rank, e.g. a1, b3, c4). Give only the list."""
        return p

    def score_answer(self, answer, entry):
        gold = set(x.strip() for x in entry.answer.split(",") if x.strip())
        try:
            parts = set(x.strip().lower() for x in str(answer).split(",") if x.strip())
        except Exception:
            return 0.0
        if not parts or parts != gold:
            return 0.0
        for x in parts:
            if len(x) != 2 or x[0] not in FILES or x[1] not in "12345678":
                return 0.0
        return 1.0
