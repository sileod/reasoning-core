import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _winding_angle(pts):
    """Winding number of a closed polygonal loop around the origin via the
    cumulative signed-angle method.  Returns exactly an integer."""
    total = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        a1 = math.atan2(y1, x1)
        a2 = math.atan2(y2, x2)
        d = a2 - a1
        while d > math.pi:
            d -= 2.0 * math.pi
        while d < -math.pi:
            d += 2.0 * math.pi
        total += d
    return int(round(total / (2.0 * math.pi)))


def _winding_ray(pts):
    """Independent winding-number check: count signed crossings of the positive
    x-axis by oriented edges.  Returns exactly an integer, equal to _winding_angle
    for any closed polygon not through the origin."""
    w = 0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > 0) != (y2 > 0):
            xint = x1 + (x2 - x1) * (0.0 - y1) / (y2 - y1)
            if xint > 0:
                w += 1 if y2 > 0 else -1
    return w


@dataclass
class BoundaryDegreeConfig(Config):
    nodes: int = 6
    wmax: int = 1

    def apply_difficulty(self, level):
        self.nodes = 6 + 3 * level
        self.wmax = 1 + (level + 1) // 2


class BoundaryDegreeInference(Task):
    summary = (
        "Combine oriented boundary pieces and nonzero piecewise-linear vector "
        "values in two or three dimensions; infer the signed interior zero count "
        "forced by the boundary and whether a zero must exist."
    )
    config_cls = BoundaryDegreeConfig
    task_version = 2

    def generate_entry(self):
        nodes = self.config.nodes
        wmax = self.config.wmax
        dim = random.choice((2, 3))

        W = random.randint(-wmax, wmax)
        rmin, rmax = 1.5, 4.5
        theta0 = random.uniform(0.0, 2.0 * math.pi)

        for _ in range(400):
            if W == 0:
                spread = random.uniform(0.4, 1.4)
                base = random.uniform(0.6, 2.4)
                pts = [
                    (random.uniform(rmin, rmax) * math.cos(base + spread * (k / (nodes - 1) - 0.5)),
                     random.uniform(rmin, rmax) * math.sin(base + spread * (k / (nodes - 1) - 0.5)))
                    for k in range(nodes)
                ]
            else:
                sweep = 2.0 * math.pi * W
                pts = []
                for k in range(nodes):
                    ang = theta0 + sweep * k / (nodes - 1)
                    r = random.uniform(rmin, rmax)
                    pts.append((r * math.cos(ang), r * math.sin(ang)))

            wa = _winding_angle(pts)
            wr = _winding_ray(pts)
            if wa == W and wr == W:
                break
        else:
            raise RuntimeError("could not realize target winding")

        if dim == 3:
            withz = [(int(round(x * 1e6)), int(round(y * 1e6)),
                      int(round(random.uniform(-2.0, 2.0) * 1e3)))
                     for (x, y) in pts]
        else:
            withz = [(int(round(x * 1e6)), int(round(y * 1e6))) for (x, y) in pts]

        fmt = "3D vectors (x,y,z)" if dim == 3 else "2D vectors (x,y)"
        boundary = ", ".join(str(v) for v in withz)
        need_zero = W != 0

        return Entry(
            metadata={
                "dim": dim,
                "boundary": boundary,
                "winding": W,
                "need_zero": need_zero,
                "nodes": nodes,
            },
            answer=str(W),
            cot=None,
        )

    def render_prompt(self, metadata):
        return (
            "An oriented closed piecewise-linear boundary is given as its ordered "
            f"list of {metadata['nodes']} nonzero boundary vector values, each "
            "taken from a continuous piecewise-linear map defined on a filled disk "
            "whose values are nonzero on the boundary.  "
            f"The oriented boundary pieces are: {metadata['boundary']}\n"
            "By the Poincare-Hopf index theorem the signed interior zero count "
            "(sum of signs of zeros of the map strictly inside the disk) equals the "
            "winding number of this boundary around the origin, and a zero must "
            "exist inside if and only if that winding number is nonzero.  "
            "Counterclockwise net winding contributes a positive increment and "
            "clockwise net winding a negative one, while no net winding is "
            "zero.  "
            "What is the signed interior zero count forced by the boundary? "
            "Answer with a single integer that may be negative, zero, or positive."
        )

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(str(answer).strip()) == int(entry.metadata["winding"]) else 0.0
        except (ValueError, TypeError, AttributeError):
            return 0.0

    def distractor_candidates(self, entry):
        w = entry.metadata["winding"]
        return [str(w + 1), str(w - 1), str(-w)]


TASK_META = {'parent_source_id': None,
 'idea': 'boundary_degree_inference (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_interacting_updates_r4/boundary_degree_inference',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1339177894,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
