import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'tilted_vessel_spillage (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_semantics_r4/tilted_vessel_spillage',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _rotate_pt(pt, cx, cy, ang):
    import math as _m
    x, y = pt
    dx, dy = x - cx, y - cy
    c, s = _m.cos(ang), _m.sin(ang)
    return (cx + dx * c - dy * s, cy + dx * s + dy * c)


def _rotate(poly, cx, cy, ang):
    return [_rotate_pt(pt, cx, cy, ang) for pt in poly]


def _clip_y(poly, ymax):
    """Sutherland-Hodgman clip of a polygon to the half-plane y <= ymax."""
    out = []
    prev = poly[-1]
    prev_in = prev[1] <= ymax + 1e-9
    for cur in poly:
        cur_in = cur[1] <= ymax + 1e-9
        if cur_in != prev_in:
            t = (ymax - prev[1]) / (cur[1] - prev[1])
            out.append((prev[0] + t * (cur[0] - prev[0]), ymax))
        if cur_in:
            out.append(cur)
        prev, prev_in = cur, cur_in
    return out


def _area(poly):
    s = 0.0
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def _cap(poly):
    """Max retainable volume: area of the basin at/below its lower rim."""
    left, right = poly[0], poly[-2]
    lower = min(left[1], right[1])
    return _area(_clip_y(poly, lower))


def _midpoint(a, b):
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


@dataclass
class TiltedVesselConfig(Config):
    n_segs: int = 2
    n_ops: int = 2
    max_rim: int = 12
    max_vol: int = 40

    def apply_difficulty(self, level):
        self.n_segs = stochastic_rounding(2 + level)
        self.n_ops = stochastic_rounding(2 + level)
        self.max_rim = stochastic_rounding(8 + level)
        self.max_vol = stochastic_rounding(25 + 20 * level)


class TiltedVessel(Task):
    summary = ("Track liquid in a polygonal basin cross-section (staircase valley, "
               "flat rim) through sequential adds of volume, tilts about the top "
               "center, and removal of an internal end wall; after each step the "
               "free surface equilibrates at the lower rim and overflow spills and "
               "is discarded, and the final answer is the integer retained volume.")
    config_cls = TiltedVesselConfig

    def generate_entry(self):
        n = self.config.n_segs
        n_ops = self.config.n_ops
        max_rim = self.config.max_rim
        max_vol = self.config.max_vol

        for _ in range(600):
            W = random.randrange(8, 18)
            rim = random.randrange(6, max_rim + 1)
            interior = [random.randrange(1, W) for _ in range(n - 1)]
            xs = sorted(set(interior + [0, W]))
            if len(xs) < 3:
                continue
            ys = [random.randrange(1, rim) for _ in range(len(xs))]

            split = random.randrange(1, len(xs) - 1)
            x_stop = xs[split]

            pre = [(0, rim)] + list(zip(xs[:split + 1], ys[:split + 1])) + [(x_stop, rim), (0, rim)]
            full = [(0, rim)] + list(zip(xs, ys)) + [(W, rim), (0, rim)]

            optypes = []
            if n_ops >= 1:
                optypes.append("add")
            if n_ops >= 2:
                optypes.append("tilt")
            if n_ops >= 3:
                optypes.append("remove_partition")
            while len(optypes) < n_ops:
                optypes.append(random.choice(["add", "tilt"]))
            random.shuffle(optypes)

            ops = []
            removed = False
            for op in optypes:
                if op == "add":
                    v = random.randrange(1, max_vol + 1)
                    ops.append(("add", v))
                elif op == "tilt":
                    ang_deg = random.choice([-1, 1]) * random.randrange(3, 26)
                    ops.append(("tilt", ang_deg))
                elif not removed:
                    ops.append(("remove_partition", 0))
                    removed = True
                else:
                    continue

            import math
            local = pre
            rot = 0.0
            V = 0.0
            for op, param in ops:
                if op == "add":
                    V += float(param)
                elif op == "tilt":
                    rot += math.radians(param)
                elif op == "remove_partition":
                    local = full
                pivot = _midpoint(local[0], local[-2])
                world = _rotate(local, pivot[0], pivot[1], rot)
                V = min(V, _cap(world))

            retained_int = int(round(V))
            if retained_int < 0:
                continue
            stated = {int(abs(p)) for _, p in ops if isinstance(p, (int, float))}
            if retained_int in stated:
                continue

            return Entry(metadata={
                "n_segs": len(xs) - 1,
                "W": W,
                "rim": rim,
                "xs": xs,
                "ys": ys,
                "x_stop": x_stop,
                "split_index": split,
                "pre_poly": pre,
                "full_poly": full,
                "ops": ops,
                "retained": retained_int,
            }, answer=str(retained_int))

        raise RuntimeError("failed to build a tilted-vessel instance")

    def render_prompt(self, metadata):
        xs = metadata["xs"]
        ys = metadata["ys"]
        rim = metadata["rim"]
        W = metadata["W"]
        x_stop = metadata["x_stop"]
        valley = " ".join("(%d,%d)" % (x, y) for x, y in zip(xs, ys))
        desc = (
            "A vessel's cross-section is a basin whose bottom is a staircase valley "
            "through the points %s (x increasing left to right), with a vertical "
            "side wall rising from the leftmost point to height %d and from the "
            "rightmost point to height %d; the two rim tops are joined straight "
            "across the open top at height %d. Its full width is %d (left rim at "
            "x=0). A removable internal wall stands at x=%d, so before it is "
            "removed the liquid is confined to the basin portion at x <= %d."
            % (valley, rim, rim, rim, W, x_stop, x_stop)
        )
        steps = []
        for op, param in metadata["ops"]:
            if op == "add":
                steps.append("add %d units of liquid" % param)
            elif op == "tilt":
                steps.append("tilt the whole cross-section by %d degrees about the "
                             "center of its top rim" % param)
            else:
                steps.append("remove the internal wall at x=%d so liquid fills the "
                             "whole vessel" % x_stop)
        op_text = ", \n".join(steps)
        return (
            "%s\n\nThe vessel starts empty. In order, apply exactly these "
            "operations, one after another:\n%s\n\nAfter every operation the "
            "liquid settles with a horizontal surface and is held by the vessel only "
            "up to the level of its lower rim; any liquid that would rise above "
            "that rim overflows and is discarded, and it cannot be recovered later. "
            "What integer amount of liquid is retained in the vessel after all "
            "operations are applied? The answer is one integer."
            % (desc, op_text)
        )

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        try:
            return 1.0 if int(float(str(answer).strip())) == int(metadata["retained"]) else 0.0
        except (ValueError, TypeError):
            if str(answer).strip() == str(metadata["retained"]):
                return 1.0
            return 0.0
