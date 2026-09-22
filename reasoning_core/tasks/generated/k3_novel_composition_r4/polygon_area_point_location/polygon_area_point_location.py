import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'polygon_area_point_location (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_novel_composition_r4/polygon_area_point_location',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Query points are generated from random integer coordinates within the polygon's bounding box, with a fixed proportion guaranteed inside, outside, and exactly on edges."


def signed_area(verts):
    return sum(verts[i][0] * verts[(i + 1) % len(verts)][1]
               - verts[(i + 1) % len(verts)][0] * verts[i][1]
               for i in range(len(verts)))


def normalize(verts):
    if signed_area(verts) < 0:
        verts = list(reversed(verts))
    return verts, signed_area(verts)


def point_on_seg(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    if (x2 - x1) * (y - y1) != (y2 - y1) * (x - x1):
        return False
    return min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2)


def point_on_edges(p, verts):
    for i in range(len(verts)):
        if point_on_seg(p, verts[i], verts[(i + 1) % len(verts)]):
            return True
    return False


def point_classify(p, verts):
    if point_on_edges(p, verts):
        return "boundary"
    x, y = p
    inside = False
    for i in range(len(verts)):
        (x1, y1), (x2, y2) = verts[i], verts[(i + 1) % len(verts)]
        if (y1 > y) != (y2 > y):
            xint = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xint > x:
                inside = not inside
    return "inside" if inside else "outside"


def make_polygon(max_vert, coord_range):
    while True:
        n = random.randint(4, max_vert)
        pulses = [random.uniform(0.4, 1.0) for _ in range(n)]
        rad = random.randint(5, coord_range)
        raw = []
        for i in range(n):
            ang = 2 * math.pi * i / n
            rr = rad * pulses[i]
            raw.append((rr * math.cos(ang), rr * math.sin(ang)))
        ints = [(int(round(x)), int(round(y))) for x, y in raw]
        if len(set(ints)) != len(ints):
            continue
        if signed_area(ints) == 0:
            continue
        minx = min(v[0] for v in ints)
        miny = min(v[1] for v in ints)
        if minx >= 0 or miny >= 0:
            continue
        return ints


def sample_point(poly, target, attempts=300):
    xs = [v[0] for v in poly]
    ys = [v[1] for v in poly]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    if target == "boundary":
        while True:
            i = random.randrange(len(poly))
            a, b = poly[i], poly[(i + 1) % len(poly)]
            t = random.random()
            p = (int(round(a[0] + t * (b[0] - a[0]))),
                 int(round(a[1] + t * (b[1] - a[1]))))
            if point_on_edges(p, poly):
                return p
            if attempts <= 0:
                break
            attempts -= 1
    for _ in range(attempts):
        p = (random.randint(minx, maxx), random.randint(miny, maxy))
        if point_classify(p, poly) == target:
            return p
    return None


@dataclass
class PolygonConfig(Config):
    min_vert: int = 4
    max_vert: int = 6
    coord_range: int = 10

    def apply_difficulty(self, level):
        self.min_vert = 4 + level
        self.max_vert = 6 + 2 * level
        self.coord_range = 10 + 4 * level


LOCATION_LABEL = {"inside": "inside", "outside": "outside", "boundary": "on the boundary"}


class PolygonAreaPointLocation(Task):
    summary = "Over simple polygons given as integer vertex lists: accumulate the shoelace cross-sum for signed area and classify query points by ray-crossing parity; answers are the doubled area or inside/outside/on-boundary."
    config_cls = PolygonConfig

    def generate_entry(self):
        while True:
            poly = make_polygon(self.config.max_vert, self.config.coord_range)
            _, area = normalize(poly)
            doubled = abs(area)
            c = random.choice(["inside", "outside", "boundary"])
            p = sample_point(poly, c)
            if p is None:
                continue
            if point_classify(p, poly) != c:
                continue
            return Entry(
                metadata={
                    "vertices": poly,
                    "point": p,
                    "doubled_area": doubled,
                    "label": c,
                },
                answer=f"{doubled} | {LOCATION_LABEL[c]}",
            )

    def render_prompt(self, metadata):
        verts = ", ".join(f"({x},{y})" for x, y in metadata["vertices"])
        px, py = metadata["point"]
        return (
            f"A simple polygon has vertices in order: [{verts}]. "
            f"A query point is at ({px},{py}). "
            f"Using the shoelace formula, the doubled signed area is the sum of "
            f"cross terms; its absolute value is the doubled area. "
            f"Ray-crossing parity classifies a point on the polygon as on the "
            f"boundary. What are the doubled area and the location of the query "
            f"point (inside, outside, or on the boundary)? "
            f"Answer as \"<doubled area> | <location>\"."
        )

    def score_answer(self, answer, entry):
        want = f"{entry.metadata['doubled_area']} | {LOCATION_LABEL[entry.metadata['label']]}"
        if answer is None:
            return 0.0
        return 1.0 if str(answer).strip() == want else 0.0
