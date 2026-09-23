import random
from bisect import bisect_right
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class BresenhamRasterTraceConfig(Config):
    level: int = 0
    max_size: int = 16

    def apply_difficulty(self, level):
        self.level = level
        self.max_size = 8 + 4 * level


def _points_on_line(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    pts = []
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return pts


def _points_on_circle(cx, cy, r):
    x, y, err = r, 0, 1 - r
    pts = []
    while x >= y:
        pts.extend([
            (cx + x, cy + y), (cx + y, cy + x),
            (cx - y, cy + x), (cx - x, cy + y),
            (cx - x, cy - y), (cx - y, cy - x),
            (cx + y, cy - x), (cx + x, cy - y),
        ])
        y += 1
        if err < 0:
            err += 2 * y + 1
        else:
            x -= 1
            err += 2 * (y - x) + 1
    return sorted(set(pts))


def _format(pts):
    return "".join(f"({x},{y})" for x, y in pts)


def _line_decisions(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    dec = []
    step = []
    while True:
        dec.append(err)
        step.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return dec, step


class BresenhamRasterTrace(Task):
    summary = "Rasterize line segments (all octants) and circles with exact integer error-term updates, returning the ordered pixel list, the pixel chosen at a queried step, or the decision value at a queried row."
    config_cls = BresenhamRasterTraceConfig
    task_version = 2

    design_choice = 'Queried output is the full ordered pixel list as a compact string of bracketed coordinate pairs, e.g. "(0,0)(1,1)(2,2)"'

    def generate_entry(self):
        cfg = self.config
        mode = random.choices(
            ["line", "circle", "query_pixel", "query_decision"],
            weights=[3, 2, 1, 1],
        )[0]
        while True:
            if mode == "line":
                while True:
                    x0 = random.randint(0, cfg.max_size)
                    y0 = random.randint(0, cfg.max_size)
                    dx = random.randint(-(cfg.max_size // 2 + 2), cfg.max_size // 2 + 2)
                    dy = random.randint(-(cfg.max_size // 2 + 2), cfg.max_size // 2 + 2)
                    if dx == 0 and dy == 0:
                        continue
                    x1 = x0 + dx
                    y1 = y0 + dy
                    if x1 < 0 or y1 < 0 or x1 > cfg.max_size + cfg.max_size // 2 or y1 > cfg.max_size + cfg.max_size // 2:
                        continue
                    pts = _points_on_line(x0, y0, x1, y1)
                    if 2 <= len(pts) <= cfg.max_size + 1:
                        break
                answer = _format(pts)
                metadata = {
                    "kind": "line",
                    "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                    "points": pts, "answer": answer,
                }
                break

            elif mode == "circle":
                while True:
                    r = random.randint(1, max(1, cfg.max_size // 3 + 1))
                    cx = random.randint(r, cfg.max_size)
                    cy = random.randint(r, cfg.max_size)
                    pts = _points_on_circle(cx, cy, r)
                    if 4 <= len(pts) <= cfg.max_size + 1:
                        break
                answer = _format(sorted(pts))
                metadata = {
                    "kind": "circle",
                    "cx": cx, "cy": cy, "r": r,
                    "points": sorted(pts), "answer": answer,
                }
                break

            elif mode == "query_pixel":
                while True:
                    x0 = random.randint(0, cfg.max_size)
                    y0 = random.randint(0, cfg.max_size)
                    dx = random.randint(-(cfg.max_size // 2 + 2), cfg.max_size // 2 + 2)
                    dy = random.randint(-(cfg.max_size // 2 + 2), cfg.max_size // 2 + 2)
                    x1 = x0 + dx
                    y1 = y0 + dy
                    if x1 < 0 or y1 < 0 or x1 > cfg.max_size + cfg.max_size // 2 or y1 > cfg.max_size + cfg.max_size // 2:
                        continue
                    pts = _points_on_line(x0, y0, x1, y1)
                    if 3 <= len(pts) <= cfg.max_size + 1:
                        break
                q = random.randint(1, len(pts) + 1)
                if q <= len(pts):
                    answer = f"({pts[q-1][0]},{pts[q-1][1]})"
                else:
                    answer = "OUT_OF_RANGE"
                metadata = {
                    "kind": "query_pixel",
                    "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                    "points": pts, "q": q, "answer": answer,
                }
                break

            else:
                while True:
                    x0 = random.randint(0, cfg.max_size)
                    y0 = random.randint(0, cfg.max_size)
                    dx = random.randint(-(cfg.max_size // 2 + 2), cfg.max_size // 2 + 2)
                    dy = random.randint(-(cfg.max_size // 2 + 2), cfg.max_size // 2 + 2)
                    if dx == 0 and dy == 0:
                        continue
                    x1 = x0 + dx
                    y1 = y0 + dy
                    if x1 < 0 or y1 < 0 or x1 > cfg.max_size + cfg.max_size // 2 or y1 > cfg.max_size + cfg.max_size // 2:
                        continue
                    dec, step = _line_decisions(x0, y0, x1, y1)
                    if 2 <= len(step) <= cfg.max_size + 1:
                        break
                q = random.randint(1, len(dec))
                answer = str(dec[q - 1])
                metadata = {
                    "kind": "query_decision",
                    "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                    "decisions": dec, "q": q, "answer": answer,
                }
                break

        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        m = metadata
        if m["kind"] == "line":
            return (
                f"Using Bresenham's line algorithm with the standard integer error term "
                f"(err initialized to dx + (-dy), updating err by -dy when 2*err >= -dy and "
                f"by dx when 2*err <= dx), rasterize the line from ({m['x0']},{m['y0']}) to "
                f"({m['x1']},{m['y1']}). Give the full ordered list of pixels from start to end "
                f"as a compact string of bracketed coordinate pairs, e.g. (0,0)(1,1)(2,2)."
            )
        if m["kind"] == "circle":
            return (
                f"Using the midpoint circle algorithm, rasterize the circle centered at "
                f"({m['cx']},{m['cy']}) with radius {m['r']}. List every integer lattice pixel "
                f"on the circle, sorted in ascending (x then y) order, as a compact string of "
                f"bracketed coordinate pairs, e.g. (0,0)(1,1)."
            )
        if m["kind"] == "query_pixel":
            return (
                f"Using Bresenham's line algorithm, rasterize the line from ({m['x0']},{m['y0']}) "
                f"to ({m['x1']},{m['y1']}). Counting steps starting at 1 (step 1 is the "
                f"({m['x0']},{m['y0']}) endpoint), which pixel is chosen at step {m['q']}? "
                f"Give the single bracketed pair, e.g. (3,4). If the line has fewer than {m['q']} "
                f"steps, answer OUT_OF_RANGE."
            )
        return (
            f"Using Bresenham's line algorithm with error term err initialized to "
            f"dx + (-dy) for the line from ({m['x0']},{m['y0']}) to ({m['x1']},{m['y1']}), "
            f"what is the integer decision value err at the start of step {m['q']} "
            f"(step 1 is the ({m['x0']},{m['y0']}) endpoint)? Give the integer only."
        )

    def score_answer(self, answer, entry):
        gold = entry["answer"]
        if isinstance(answer, str):
            return 1.0 if answer.strip() == gold else 0.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'bresenham_raster_trace (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_inference_modes_r4/bresenham_raster_trace',
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
