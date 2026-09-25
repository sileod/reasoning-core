import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'nested_radical_continuation (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_shortcuts_fail_r4/nested_radical_continuation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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


@dataclass
class _Config(Config):
    num_points: int = 2
    turns: int = 2
    max_step: int = 3

    def apply_difficulty(self, level):
        self.num_points = 2 + level
        self.turns = 2 + level
        self.max_step = 3 + level


def _winding(verts, px, py):
    wn = 0
    n = len(verts)
    for i in range(n):
        x0, y0 = verts[i]
        x1, y1 = verts[(i + 1) % n]
        if y0 <= py:
            if y1 > py:
                left = (x1 - x0) * (py - y0) - (y1 - y0) * (px - x0)
                if left > 0:
                    wn += 1
        else:
            if y1 <= py:
                left = (x1 - x0) * (py - y0) - (y1 - y0) * (px - x0)
                if left < 0:
                    wn -= 1
    return wn


def _on_segment(a, b, p):
    x0, y0 = a
    x1, y1 = b
    px, py = p
    if x0 == x1:
        return px == x0 and min(y0, y1) <= py <= max(y0, y1)
    if y0 == y1:
        return py == y0 and min(x0, x1) <= px <= max(x0, x1)
    return False


def _on_path(verts, p):
    n = len(verts)
    for i in range(n):
        if _on_segment(verts[i], verts[(i + 1) % n], p):
            return True
    return False


def _gen_loop(turns, max_step):
    W = (turns + 1) * max_step
    H = turns * max_step
    xs = sorted(random.sample(range(1, W), turns)) + [W]
    xs = [0] + xs
    ys = random.sample(range(1, H + 1), turns)
    verts = [(0, 0)]
    cur_x = 0
    for i in range(turns):
        verts.append((cur_x, ys[i]))
        cur_x = xs[i + 1]
        verts.append((cur_x, ys[i]))
    verts.append((cur_x, 0))
    if random.random() < 0.5:
        verts = [(x, -y) for (x, y) in verts]
    ox = random.randint(0, max_step)
    oy = random.randint(0, max_step)
    ox = ox if random.random() < 0.5 else -ox
    oy = oy if random.random() < 0.5 else -oy
    verts = [(x + ox, y + oy) for (x, y) in verts]
    return verts


def _gen_instance(num_points, turns, max_step, base_attempts=40):
    attempts = 0
    while True:
        attempts += 1
        if attempts > base_attempts:
            raise RuntimeError("nested_radical_continuation: no valid instance")
        verts = _gen_loop(turns, max_step)
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        inside = []
        outside = []
        for x in range(minx, maxx + 1):
            for y in range(miny, maxy + 1):
                p = (x, y)
                if _on_path(verts, p):
                    continue
                w = _winding(verts, x, y)
                if w != 0:
                    inside.append((p, w))
                else:
                    outside.append(p)
        if not inside or not outside:
            continue
        random.shuffle(inside)
        random.shuffle(outside)
        n_in = random.randint(1, min(num_points - 1, len(inside)))
        n_out = num_points - n_in
        if n_out < 1 or n_out > len(outside):
            continue
        pts = [p for (p, _w) in inside[:n_in]] + outside[:n_out]
        random.shuffle(pts)
        pts.sort(key=lambda q: (q[0], q[1]))
        windings = [_winding(verts, p[0], p[1]) for p in pts]
        return verts, pts, windings


class NestedRadicalContinuation(Task):
    summary = ("Continue nested square-root expressions along closed axis-aligned "
               "simple polygonal paths on a grid; branch points sit on grid points off "
               "the path and the oriented loop's signed winding number around each "
               "(taking values in {-1, 0, +1}) is reported as a comma-separated integer "
               "sequence, varying polygon shape, orientation, shift, branch-point count "
               "and loop order.")
    design_choice = ("Choose the polygon vertices on a fixed grid so branch cuts align "
                     "with grid lines, and the answer is the net winding number of the "
                     "loop around each branch point, returned as a signed integer "
                     "sequence.")
    config_cls = _Config

    def generate_entry(self):
        verts, pts, windings = _gen_instance(
            self.config.num_points, self.config.turns, self.config.max_step)
        metadata = {
            "vertices": [list(v) for v in verts],
            "branch_points": [list(p) for p in pts],
            "windings": [int(w) for w in windings],
            "num_points": int(self.config.num_points),
        }
        answer = ", ".join(str(int(w)) for w in windings)
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        vert_lines = "; ".join(f"({x},{y})" for x, y in metadata["vertices"])
        pt_lines = " | ".join(f"B{i+1}=({x},{y})"
                              for i, (x, y) in enumerate(metadata["branch_points"]))
        return (
            "A nested square-root expression extends along the complex plane and has "
            "branch points at the following grid locations, where a branch cut on each "
            "aligns with the grid lines:\n"
            f"{pt_lines}\n"
            "An oriented closed polygonal path is drawn on the same grid, tracing the "
            "vertices in order and then returning to the first (every segment is "
            "axis-aligned and the path avoids the branch points and their cuts):\n"
            f"{vert_lines}\n"
            "Following the nested radical once around this closed path, the endpoint "
            "branch relative to the starting branch changes by the net number of times "
            "the oriented loop winds around each branch point. Report the net signed "
            "winding number of the loop around each branch point, in the order B1, B2, "
            "..., as a single comma-separated sequence of signed integers, e.g. "
            "1, 0, -1."
        )

    def score_answer(self, answer, entry):
        return 1.0 if _norm_seq(answer or "") == _norm_seq(entry.answer) else 0.0


def _norm_seq(s):
    return ",".join(t.strip() for t in s.split(",") if t.strip())
