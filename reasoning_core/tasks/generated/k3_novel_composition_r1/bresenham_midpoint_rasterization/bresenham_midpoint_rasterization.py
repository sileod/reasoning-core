import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class BresenhamConfig(Config):
    max_coord: int = 12
    min_len: int = 3
    max_len: int = 15

    def apply_difficulty(self, level):
        self.max_coord = 12 + 8 * level
        self.min_len = 3 + level // 3
        self.max_len = 12 + 3 * level


def midpoint_points(x0, y0, x1, y1):
    """Return the ordered lattice points rasterized by the standard textbook
    Bresenham midpoint algorithm for an arbitrary integer segment. The dither /
    tie-break rule is fixed: for the major axis we move one each step and add the
    minor axis move when the error accumulator crosses zero. This uniquely defines
    the point sequence for any octant and is deterministic and reproducible.
    """
    dx = x1 - x0
    dy = y1 - y0
    sx = 1 if dx >= 0 else -1
    sy = 1 if dy >= 0 else -1
    adx = abs(dx)
    ady = abs(dy)

    points = []
    if adx >= ady:
        err = adx // 2
        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1:
                break
            err -= ady
            if err < 0:
                y += sy
                err += adx
            x += sx
    else:
        err = ady // 2
        x, y = x0, y0
        while True:
            points.append((x, y))
            if y == y1:
                break
            err -= adx
            if err < 0:
                x += sx
                err += ady
            y += sy
    return points


def _format_points(points):
    return ",".join(f"({x},{y})" for (x, y) in points)


def _parse_points(answer):
    """Parse a comma-separated list of (x,y) pairs into a list of int tuples."""
    if not answer or any(ch.isspace() for ch in answer):
        return None
    try:
        pts = []
        for tok in answer.split(","):
            tok = tok.strip()
            if not (tok.startswith("(") and tok.endswith(")")):
                return None
            xs, ys = tok[1:-1].split(",")
            pts.append((int(xs), int(ys)))
        return pts
    except Exception:
        return None


class BresenhamMidpointRasterization(Task):
    summary = ("Rasterize integer-endpoint segments by the midpoint error-term rule, "
               "stepping the major axis and conditionally the minor across varied octants; "
               "answers are the ordered lattice points along the drawn segment.")
    design_choice = ("Answer format: return the full ordered list of rasterized lattice "
                     "points for the segment.")
    config_cls = BresenhamConfig
    task_version = 2

    def generate_entry(self):
        while True:
            mc = self.config.max_coord
            x0 = random.randint(0, mc)
            y0 = random.randint(0, mc)
            dx = random.randint(-mc, mc)
            dy = random.randint(-mc, mc)
            if dx == 0 and dy == 0:
                continue
            x1 = x0 + dx
            y1 = y0 + dy
            if not (0 <= x1 <= mc and 0 <= y1 <= mc):
                continue
            pts = midpoint_points(x0, y0, x1, y1)
            if not (self.config.min_len <= len(pts) <= self.config.max_len):
                continue
            answer = _format_points(pts)
            return Entry(metadata={"x0": x0, "y0": y0, "x1": x1, "y1": y1,
                                   "points": pts},
                         answer=answer)

    def render_prompt(self, metadata):
        x0, y0, x1, y1 = metadata["x0"], metadata["y0"], metadata["x1"], metadata["y1"]
        return (f"Using Bresenham's midpoint line-drawing algorithm (the standard "
                f"textbook variant), rasterize the integer segment from ({x0},{y0}) to "
                f"({x1},{y1}) on the integer lattice. Give the answer as the segment's "
                f"ordered list of lattice points from start to end: each point as (x,y), "
                f"consecutive points separated by a comma with no spaces, e.g. "
                f"(1,1),(1,2),(1,3).")


def _parse_answer(answer):
    return _parse_points(answer)


def score_answer(answer, entry):
    parsed = _parse_points(answer)
    if parsed is None:
        return 0.0
    gold = [tuple(p) for p in entry.metadata["points"]]
    if parsed == gold:
        return 1.0
    return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'bresenham_midpoint_rasterization (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_novel_composition_r1/bresenham_midpoint_rasterization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
