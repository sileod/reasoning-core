import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'stereochemical_parity_transport (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/stereochemical_parity_transport',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_POOL = list("ABCDEFGH")


@dataclass
class ParityTransportConfig(Config):
    n_ops: int = 2

    def apply_difficulty(self, level):
        self.n_ops = 2 + 2 * level


def _sign_of_perm(perm, order):
    """+1 for even, -1 for odd permutation, relative to rank in `order`."""
    rank = {lig: i for i, lig in enumerate(order)}
    vals = [rank[lig] for lig in perm]
    inversions = 0
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            if vals[i] > vals[j]:
                inversions += 1
    return -1 if inversions % 2 else 1


def _chirality(perm, order):
    return "R" if _sign_of_perm(perm, order) == 1 else "S"


def _apply_swap(perm, a, b):
    i, j = perm.index(a), perm.index(b)
    perm[i], perm[j] = perm[j], perm[i]


def _apply_rotate(perm, a, b, c):
    pa, pb, pc = perm.index(a), perm.index(b), perm.index(c)
    perm[pb], perm[pc], perm[pa] = a, b, c


def _apply_invert(perm):
    perm[0], perm[1] = perm[1], perm[0]


def _parse_answer(answer):
    if not isinstance(answer, str):
        return None
    a = answer.strip().upper()
    if a in ("R", "S"):
        return a
    return None


def _render_ops(ops):
    lines = []
    for idx, op in enumerate(ops, 1):
        tag = op[0]
        if tag == "swap":
            lines.append(f"  {idx}. swap {op[1]} {op[2]}")
        elif tag == "rotate":
            lines.append(f"  {idx}. rotate {op[1]} {op[2]} {op[3]}")
        else:
            lines.append(f"  {idx}. invert")
    return "\n".join(lines)


class ParityTransportV3(Task):
    task_name = "parity_transport"
    summary = ("Track a tetrahedral center's handedness through composed ligand "
               "exchanges (swap), proper 3-rotations (rotate), and reflections "
               "(invert) over an ordered-neighbor representation; return the "
               "derived final R/S parity from the sign of the composed permutation.")
    config_cls = ParityTransportConfig
    task_version = 2

    def generate_entry(self):
        letters = random.sample(_POOL, 4)
        order = sorted(letters)
        perm = random.sample(letters, 4)

        ops = []
        for _ in range(self.config.n_ops):
            r = random.random()
            if r < 0.40:
                a, b = random.sample(letters, 2)
                ops.append(["swap", a, b])
            elif r < 0.80:
                a, b, c = random.sample(letters, 3)
                ops.append(["rotate", a, b, c])
            else:
                ops.append(["invert"])

        work = list(perm)
        sign_total = _sign_of_perm(perm, order)
        for op in ops:
            tag = op[0]
            if tag == "swap":
                _apply_swap(work, op[1], op[2])
                sign_total *= -1
            elif tag == "rotate":
                _apply_rotate(work, op[1], op[2], op[3])
            else:
                _apply_invert(work)
                sign_total *= -1

        sim_chir = _chirality(work, order)
        assert sim_chir == ("R" if sign_total == 1 else "S"), (
            "simulated configuration and parity-tracking signs disagree"
        )
        assert sim_chir in ("R", "S")

        metadata = {
            "letters": sorted(letters),
            "initial": list(perm),
            "ops": ops,
            "n_ops": self.config.n_ops,
        }
        return Entry(metadata=metadata, answer=sim_chir)

    def render_prompt(self, metadata):
        ops_block = _render_ops(metadata["ops"])
        return (
            "A tetrahedral chiral center bears four distinct substituents. Its "
            "current spatial arrangement is given as the ordered neighbor list "
            f"{metadata['initial']!r}, meaning the substituent at slot 0 is "
            f"{metadata['initial'][0]}, at slot 1 is {metadata['initial'][1]}, "
            f"at slot 2 is {metadata['initial'][2]}, at slot 3 is "
            f"{metadata['initial'][3]} (slots in clockwise order viewed from "
            "above). Taking the reference order as the alphabetical order of the "
            f"four substituents ({sorted(metadata['letters'])!r}), the center's "
            "chirality is R when its neighbor list is an even permutation of that "
            "reference order and S when it is an odd one.\n\n"
            "The following operations are then applied to the center in order:\n"
            f"{ops_block}\n\n"
            "Here swap X Y exchanges the two listed neighboring substituents "
            "(this flips handedness), rotate X Y Z cyclically moves X to Y's "
            "slot, Y to Z's slot, and Z to X's slot (this preserves handedness), "
            "and invert reflects the center in a mirror plane (this flips "
            "handedness).\n\n"
            "Give the chirality of the center after all operations as a single "
            "letter."
        )

    def score_answer(self, answer, entry):
        ref = _parse_answer(entry["answer"])
        got = _parse_answer(answer)
        if ref is None or got is None:
            return 0.0
        return 1.0 if got == ref else 0.0
