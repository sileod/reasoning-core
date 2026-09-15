import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _perm_cycles(perm):
    """Return the cycle structure of a permutation given as mapping index -> image (0-based).

    Fixed points are kept as 1-cycles. Results are a list of cycles, each a tuple of
    positions, sorted stably so that identical group elements render identically.
    """
    n = len(perm)
    seen = [False] * n
    cycles = []
    for start in range(n):
        if seen[start]:
            continue
        cyc = []
        cur = start
        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)
            cur = perm[cur]
        cycles.append(tuple(cyc))
    cycles.sort(key=lambda c: (min(c), tuple(c)))
    return cycles


def _render_cycle(cycle):
    return "(" + " ".join(str(x + 1) for x in cycle) + ")"


def _render_perm(perm):
    return "".join(_render_cycle(c) for c in _perm_cycles(perm))


def _count_fixed_colorings(perm, colors):
    """Number of colorings fixed by perm = colors ** (#cycles(perm))."""
    return colors ** len(_perm_cycles(perm))


def _necklace_group(n):
    """Cyclic group on n positions (rotations)."""
    perms = []
    for k in range(n):
        perms.append([(i + k) % n for i in range(n)])
    return perms


def _bracelet_group(n):
    """Dihedral group on n positions (rotations + reflections)."""
    perms = []
    for k in range(n):
        perms.append([(i + k) % n for i in range(n)])
    for k in range(n):
        perms.append([(k - i) % n for i in range(n)])
    return perms


def _grid_group(m, n):
    """Dihedral (V4) group of a rectangle acting on m*n cells, row-major order.

    cell (r, c) -> index r * n + c.
    Symmetries: identity, 180-degree rotation, horizontal flip, vertical flip.
    """
    perms = []
    size = m * n
    identity = [i for i in range(size)]
    rot180 = [0] * size
    flip_h = [0] * size
    flip_v = [0] * size
    for r in range(m):
        for c in range(n):
            idx = r * n + c
            rot180[idx] = (m - 1 - r) * n + (n - 1 - c)
            flip_h[idx] = (m - 1 - r) * n + c
            flip_v[idx] = r * n + (n - 1 - c)
    for perm in (identity, rot180, flip_h, flip_v):
        perms.append(perm)
    return perms


@dataclass
class BurnsideOrbitCountConfig(Config):
    min_n: int = 2
    max_n: int = 4
    min_colors: int = 2
    max_colors: int = 3
    families: tuple = ("necklace", "bracelet", "grid")
    min_grid: int = 2
    max_grid: int = 3
    max_grid_colors: int = 3

    def apply_difficulty(self, level):
        self.min_n = 2
        self.max_n = min(5 + level, 10)
        self.max_colors = min(5 + level, 7)
        self.min_grid = 2
        self.max_grid = min(4 + level, 6)
        self.max_grid_colors = min(5 + level, 7)


def _build_instance(config):
    family = random.choice(config.families)
    if family == "necklace":
        n = random.randint(config.min_n, config.max_n)
        colors = random.randint(config.min_colors, config.max_colors)
        perms = _necklace_group(n)
        return "necklace", perms, colors, n
    if family == "bracelet":
        n = random.randint(max(config.min_n, 3), max(config.max_n, 3))
        colors = random.randint(config.min_colors, config.max_colors)
        perms = _bracelet_group(n)
        return "bracelet", perms, colors, n
    m = random.randint(config.min_grid, config.max_grid)
    n = random.randint(config.min_grid, config.max_grid)
    colors = random.randint(config.min_colors, config.max_grid_colors)
    perms = _grid_group(m, n)
    return "grid", perms, colors, (m, n)


def score_burnside(answer, elementary):
    """Return 1.0 if answer is the simplified fraction of the orbit count.

    elementary is the list of fixed-color counts c^cycles(g) for each group
    element; the orbit count is their average.
    """
    from fractions import Fraction as F
    gold = F(sum(elementary), len(elementary))
    try:
        got = F(str(answer).strip())
    except Exception:
        return 0.0
    return 1.0 if got == gold else 0.0


class BurnsideOrbitCount(Task):
    summary = ("Count orbits of necklaces, bracelets, or rectangular grids under their cyclic, "
               "dihedral, or rectangle-symmetry groups by averaging c^cycles over group elements "
               "given in cycle notation, returning the simplified fraction for a stated color count.")
    design_choice = ("Present the group as a list of permutations in cycle notation, and require "
                     "the solver to compute the cycle index and apply it to a given color count, "
                     "outputting a simplified fraction.")
    config_cls = BurnsideOrbitCountConfig

    def generate_entry(self):
        family, perms, colors, size = _build_instance(self.config)
        if family in ("necklace", "bracelet"):
            n = size
        else:
            m, n = size
        rendered = [_render_perm(p) for p in perms]
        total = sum(_count_fixed_colorings(p, colors) for p in perms)
        gold = Fraction(total, len(perms))
        answer = "%d/%d" % (gold.numerator, gold.denominator)
        orbits = gold.numerator // gold.denominator
        assert orbits >= 1 and Fraction(orbits, 1) == gold
        metadata = {
            "family": family,
            "colors": int(colors),
            "size": (int(m), int(n)) if family == "grid" else int(n),
            "n_positions": int(perms[0].__len__()),
            "group_size": int(len(perms)),
            "perms_cycle_notation": rendered,
            "elementary": [int(_count_fixed_colorings(p, colors)) for p in perms],
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def score_answer(self, answer, entry):
        return score_burnside(answer, entry.metadata["elementary"])

    def render_prompt(self, metadata):
        family = metadata["family"]
        colors = metadata["colors"]
        renders = metadata["perms_cycle_notation"]
        if family == "necklace":
            obj = "a necklace of %d beads" % int(metadata["size"])
        elif family == "bracelet":
            obj = "a bracelet of %d beads" % int(metadata["size"])
        else:
            m, n = metadata["size"]
            obj = "a %d by %d grid of cells" % (int(m), int(n))
        lines = [
            "The symmetry group of %s has %d elements. Each element is a permutation of the "
            "positions, written in cycle notation over the positions numbered 1 to %d (a "
            "one-cycle like (3) is a fixed point)." % (obj, metadata["group_size"],
                                                      metadata["n_positions"])
        ]
        lines.append("Group elements:")
        for r in renders:
            lines.append(r)
        lines.append("Color each position with one of %d available colors."
                     % colors)
        lines.append("Using Burnside's lemma, count the distinct colorings up to symmetry "
                     "(the number of orbits), averaging the number of arrangements each group "
                     "element leaves unchanged over all %d group elements."
                     % metadata["group_size"])
        lines.append("Give the answer as a single simplified fraction p/q in lowest terms "
                     "(write an integer n as n/1).")
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'burnside_orbit_count (draw 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/burnside_orbit_count',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
