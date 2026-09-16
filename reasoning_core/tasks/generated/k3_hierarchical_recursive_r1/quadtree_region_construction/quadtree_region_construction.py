import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'quadtree_region_construction (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/quadtree_region_construction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _to_quadtree(grid, r0, c0, size):
    if size == 1:
        return 'B' if grid[r0][c0] else 'W'
    half = size // 2
    sub = []
    for dr, dc in ((0, 0), (0, half), (half, 0), (half, half)):
        sub.append(_to_quadtree(grid, r0 + dr, c0 + dc, half))
    if all(s == 'B' for s in sub):
        return 'B'
    if all(s == 'W' for s in sub):
        return 'W'
    return 'G' + ''.join(sub)


def _build_grid(encoding, r0, c0, size):
    grids = []
    for r in range(r0, r0 + size):
        grids.append([0] * size)
    grids = [g for g in grids]
    _fill(grids, encoding, r0, c0, size)
    return grids


def _fill(grid, enc, r0, c0, size):
    ch = enc[0]
    if size == 1:
        grid[r0][c0] = 1 if ch == 'B' else 0
        return 1
    half = size // 2
    if ch == 'B':
        for r in range(r0, r0 + size):
            for c in range(c0, c0 + size):
                grid[r][c] = 1
        return 1
    if ch == 'W':
        return 1
    # gray
    pos = 1
    for dr, dc in ((0, 0), (0, half), (half, 0), (half, half)):
        pos += _fill(grid, enc[pos:], r0 + dr, c0 + dc, half)
    return pos


def _render_grid(grid):
    return '\n'.join(''.join('#' if v else '.' for v in row) for row in grid)


@dataclass
class QuadtreeConfig(Config):
    min_size: int = 2
    max_size: int = 8
    density_low: float = 0.2
    density_high: float = 0.8
    locality: float = 0.6

    def apply_difficulty(self, level):
        self.min_size = 2 + level
        self.max_size = 4 + level * 2
        self.max_size = min(self.max_size, 16)
        self.density_high = 0.75
        self.locality = min(0.6 + level * 0.05, 0.8)


class QuadtreeRegionConstruction(Task):
    summary = "Recursively subdivide binary grids into region quadtrees, merging uniform quadrants and splitting mixed ones down to single cells; inputs vary grid size, density, and pattern locality; answer is the nested encoding."
    design_choice = "Encode the quadtree as a pre-order string of tokens: 'B' for black uniform, 'W' for white uniform, and 'G' followed by four child encodings for gray nodes."
    config_cls = QuadtreeConfig

    def generate_entry(self):
        cfg = self.config
        size = random.choice([s for s in (2, 4, 8, 16) if cfg.min_size <= s <= cfg.max_size])
        # start from a blank grid and paint random rectangles for locality
        grid = [[0] * size for _ in range(size)]
        density = random.uniform(cfg.density_low, cfg.density_high)
        area = size * size
        target_black = int(area * density)
        black = 0
        # paint rectangles
        attempts = 0
        while black < target_black and attempts < 200:
            attempts += 1
            if random.random() < cfg.locality:
                w = random.randint(1, max(1, size // 2))
                h = random.randint(1, max(1, size // 2))
                r = random.randint(0, size - h)
                c = random.randint(0, size - w)
                count = 0
                for rr in range(r, r + h):
                    for cc in range(c, c + w):
                        if grid[rr][cc] == 0:
                            grid[rr][cc] = 1
                            count += 1
                black += count
            else:
                r = random.randint(0, size - 1)
                c = random.randint(0, size - 1)
                if grid[r][c] == 0:
                    grid[r][c] = 1
                    black += 1
        # ensure not uniform entirely white or black
        if black == 0 or black == area:
            grid[0][0] = 1 - grid[0][0]
            black = 1 if black == 0 else area - 1

        enc = _to_quadtree(grid, 0, 0, size)
        # reconstruct and verify
        rebuilt = _build_grid(enc, 0, 0, size)
        assert rebuilt == grid
        return Entry(metadata={"grid": _render_grid(grid), "size": size, "encoding": enc}, answer=enc)

    def render_prompt(self, metadata):
        grid = metadata["grid"]
        size = metadata["size"]
        return (
            f"Consider the {size}x{size} binary grid below, where '#' is black (occupied) and '.' is "
            f"white (empty):\n{grid}\n\n"
            "Build its region quadtree by recursively subdividing the square into four equal quadrants "
            "(top-left, top-right, bottom-left, bottom-right). A quadrant that is entirely black encodes "
            "as 'B', entirely white encodes as 'W', and a mixed quadrant encodes as 'G' followed by the "
            "encodings of its four children in order, recursing down to single cells. The whole grid is "
            "always non-uniform, so its root is 'G'. "
            "Give the pre-order string encoding of the root quadtree (W and B are always leaves; G always "
            "has exactly four children). The answer is just the token string."
        )


def _parse_answer(answer):
    return answer.strip().upper()


def _reconstruct_and_compare(grid, enc):
    """Verify that enc's grid equals grid. Returns bool."""
    rebuilt = _build_grid(enc, 0, 0, len(grid))
    return rebuilt == grid


def score_answer(answer, entry):
    s = _parse_answer(answer)
    grid = entry.metadata["grid"].split("\n")
    grid = [[1 if c == '#' else 0 for c in row] for row in grid]
    if s == entry.answer:
        return 1.0
    if _reconstruct_and_compare(grid, s):
        return 1.0
    return 0.0
