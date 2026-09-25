import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'figure_symmetry_audit (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_psychometrics_r5/figure_symmetry_audit',
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

design_choice = "Answer as a canonical string listing axes (e.g., 'H,V,D1,D2') and rotation orders (e.g., '2,4') for the given figure; no defect detection needed."


@dataclass
class FigureSymmetryAuditConfig(Config):
    """Difficulty scaling: larger grids, more cells, richer symmetry sets."""
    size: int = 5
    max_cells: int = 14

    def apply_difficulty(self, level):
        self.size = self.size + level
        self.max_cells = min(self.max_cells + 2 * level, self.size * self.size)


AXES = ['H', 'V', 'D1', 'D2']

_SML = [
    'H', 'V', 'D1', 'D2',
    'R2', 'R4',
    'H,R2', 'V,R2', 'D1,R2', 'D2,R2',
    'H,V', 'H,V,R2', 'H,V,R4',
    'D1,D2', 'D1,D2,R2', 'D1,D2,R4',
    'H,V,D1,D2', 'H,V,D1,D2,R2', 'H,V,D1,D2,R4',
]


def _group_orbit(cells, transform):
    """Minimal group orbit closure under the given generators (transform applied repeatedly)."""
    out = set()
    cur = set(cells)
    while cur not in out:
        out = out | cur
        nxt = set()
        for (r, c) in cur:
            nxt.add(transform(r, c))
        cur = nxt
    return frozenset(out)


def _canonical(cells):
    pts = sorted(set(cells))
    mr = min(r for r, c in pts)
    mc = min(c for r, c in pts)
    return frozenset((r - mr, c - mc) for r, c in pts)


def _reflect_h(r, c, size):
    return (size - 1 - r, c)


def _reflect_v(r, c, size):
    return (r, size - 1 - c)


def _reflect_d1(r, c, size):
    return (c, r)


def _reflect_d2(r, c, size):
    s = size - 1
    return (s - c, s - r)


def _rot90(r, c, size):
    s = size - 1
    return (c, s - r)


def _generate_base(seed_state, config):
    """Return a base polyomino whose full symmetry set is recorded."""
    # We build a symmetric cell set by choosing a fundamental domain and
    # closing under the chosen symmetry group, then recover the symmetry set.
    # First pick a target symmetry set from the small list.
    target = random.choice(_SML)
    has_r4 = 'R4' in target
    has_h = 'H' in target
    has_v = 'V' in target
    has_d1 = 'D1' in target
    has_d2 = 'D2' in target

    generators = []
    if has_r4:
        generators.append(lambda r, c: _rot90(r, c, config.size))
    if has_h:
        generators.append(lambda r, c: _reflect_h(r, c, config.size))
    if has_v:
        generators.append(lambda r, c: _reflect_v(r, c, config.size))
    if has_d1:
        generators.append(lambda r, c: _reflect_d1(r, c, config.size))
    if has_d2:
        generators.append(lambda r, c: _reflect_d2(r, c, config.size))

    # fundamental domain: pick cells in the first quadrant region
    s = config.size
    for _attempt in range(200):
        domain = set()
        n_try = random.randint(2, 4)
        for _ in range(n_try):
            r = random.randrange(s)
            c = random.randrange(s)
            domain.add((r, c))
        if not domain:
            continue
        # build one representative of each generator (compose)
        reps = set()
        for (r, c) in domain:
            reps.add((r, c))
        if has_h:
            reps.add(_reflect_h(*list(domain)[0], s))
        if has_v:
            reps.add(_reflect_v(*list(domain)[0], s))
        if has_d1:
            reps.add(_reflect_d1(*list(domain)[0], s))
        if has_d2:
            reps.add(_reflect_d2(*list(domain)[0], s))
        if has_r4:
            reps.add(_rot90(*list(domain)[0], s))
        cells = set(domain) | reps
        # close under group
        closed = set(cells)
        changed = True
        while changed:
            changed = False
            add = set()
            for (r, c) in closed:
                for g in generators:
                    nr, nc = g(r, c)
                    if 0 <= nr < s and 0 <= nc < s:
                        add.add((nr, nc))
            before = len(closed)
            closed |= add
            if len(closed) != before:
                changed = True
        if len(closed) > config.max_cells or len(closed) < 2:
            continue
        if len(closed) > config.max_cells:
            continue
        # compute actual symmetry set of closed figure
        syms = _symmetry_set(closed, config.size)
        sym_str = _sym_str(syms, has_r4 and 'R4' in syms)
        # require the target to be achievable; accept the actual computed set
        return closed, syms
    raise RuntimeError('failed to generate symmetric figure')


def _symmetry_set(cells, size):
    s = size
    syms = []
    if all((s - 1 - r, c) in cells for (r, c) in cells):
        syms.append('H')
    if all((r, s - 1 - c) in cells for (r, c) in cells):
        syms.append('V')
    if all((c, r) in cells for (r, c) in cells):
        syms.append('D1')
    if all((s - 1 - c, s - 1 - r) in cells for (r, c) in cells):
        syms.append('D2')
    return syms


def _rot_order(cells, size):
    s = size
    r4 = frozenset((c, s - 1 - r) for (r, c) in cells)
    if r4 == frozenset(cells):
        return 4
    r2 = frozenset((s - 1 - r, s - 1 - c) for (r, c) in cells)
    if r2 == frozenset(cells):
        return 2
    return 1


def _sym_str(syms, rot_order):
    parts = list(syms)
    return ','.join(parts)


def _render_figure(cells, size):
    grid = [['.'] * size for _ in range(size)]
    for (r, c) in cells:
        grid[r][c] = 'X'
    return '\n'.join(''.join(row) for row in grid)


class FigureSymmetryAudit(Task):
    task_name = "figure_symmetry_audit"
    summary = ("Generated polyominoes and dot grids, possibly with one defect: list all "
               "reflection axes (H,V,D1,D2) and rotation orders (2,4) that leave the figure "
               "invariant, or name the minimal cells to add so the figure gains a stated "
               "symmetry.")
    config_cls = FigureSymmetryAuditConfig
    input_style = "grid"

    def generate_entry(self):
        config = self.config
        cells, syms = _generate_base(random, config)
        size = config.size
        rot = _rot_order(cells, size)
        rot_str = '1' if rot == 1 else str(rot)
        axis_str = ','.join(syms) if syms else 'None'
        answer = f"A:{axis_str};R:{rot_str}"
        figure = _render_figure(cells, size)
        metadata = {
            'size': size,
            'figure_text': figure,
            'syms': syms,
            'rot': rot,
            'answer': answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            f"The figure below is a {metadata['size']}x{metadata['size']} grid where 'X' "
            f"marks filled cells and '.' empty cells.\n{metadata['figure_text']}\n"
            f"List the reflection axes (H=horizontal, V=vertical, D1=diagonal top-left to "
            f"bottom-right, D2=diagonal top-right to bottom-left) that map the filled cells "
            f"exactly onto themselves, and the rotation order (2 for 180 degrees, 4 for 90 "
            f"degrees, or 1 if there is no rotational symmetry). Give axes first then rotation, "
            f"as A:V,H;R:4. If no axes apply, write A:None."
        )

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().replace(' ', '') == gold.strip() else 0.0
