import random
import re
from dataclasses import dataclass
from math import ceil

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'block_pile_surface_accounting (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_psychometrics_r1/block_pile_surface_accounting',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class BlockPileSurfaceAccountingV2Config(Config):
    width: int = 3
    depth: int = 3
    max_height: int = 2

    def apply_difficulty(self, level):
        self.width = ceil(3 + 0.5 * level)
        self.depth = ceil(3 + 0.5 * level)
        self.max_height = ceil(2 + 0.7 * level)


def _draw_heights(width, depth, max_height):
    mode = random.choice(("rough", "terraced", "plateau"))
    base = random.randint(1, max_height)
    density = random.uniform(0.55, 1.0)
    heights = []
    for x in range(width):
        row = []
        for y in range(depth):
            if mode == "rough":
                h = random.randint(1, max_height)
            elif mode == "terraced":
                h = max(1, min(max_height, base + min(x, y) - random.randrange(2)))
            else:
                h = base if random.random() < 0.8 else random.randint(1, max_height)
            row.append(h if random.random() < density else 0)
        heights.append(row)
    if not any(h for row in heights for h in row):
        heights[random.randrange(width)][random.randrange(depth)] = base
    return heights


def _occupied_cells(heights):
    return {(x, y, z) for x, row in enumerate(heights)
            for y, h in enumerate(row) for z in range(h)}


def _exposure_counts(cells):
    counts = [0] * 6
    for x, y, z in sorted(cells):
        assert z >= 0 and (z == 0 or (x, y, z - 1) in cells)
        neighbours = ((x + 1, y, z), (x - 1, y, z),
                      (x, y + 1, z), (x, y - 1, z), (x, y, z + 1))
        counts[sum(p not in cells for p in neighbours)] += 1
    return counts


def _column_profile(heights):
    width, depth = len(heights), len(heights[0])
    counts = [0] * 6
    for x, row in enumerate(heights):
        for y, h in enumerate(row):
            if not h:
                continue
            adjacent = [heights[a][b] if 0 <= a < width and 0 <= b < depth else 0
                        for a, b in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))]
            cuts = sorted({1, h, h + 1} | {n + 1 for n in adjacent if 0 < n < h})
            for lo, hi in zip(cuts, cuts[1:]):
                k = sum(n < lo for n in adjacent) + (lo == h)
                counts[k] += hi - lo
    return counts


def _parse_profile(answer):
    if not isinstance(answer, str) or not re.fullmatch(r"\s*[0-9]+(?:\s*,\s*[0-9]+){5}\s*", answer):
        return None
    try:
        return [int(v) for v in answer.split(",")]
    except ValueError:
        return None


class BlockPileSurfaceAccounting(Task):
    summary = "Piles of unit cubes given as column height maps or cube coordinate lists, on bounded or open floors: report counts for all exposure classes 0..5, including fully hidden interior cubes."
    design_choice = "Answer as a canonical list of counts per exposure class (0..5 faces), sorted by face count, for every instance in a level."
    config_cls = BlockPileSurfaceAccountingV2Config
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        heights = _draw_heights(cfg.width, cfg.depth, cfg.max_height)
        cells = _occupied_cells(heights)
        counts = _exposure_counts(cells)
        assert counts == _column_profile(heights)
        assert sum(counts) == len(cells) == sum(map(sum, heights))
        assert all(isinstance(c, int) and c >= 0 for c in counts)
        metadata = {
            "heights": heights,
            "coordinates": [list(p) for p in sorted(cells)],
            "representation": "coordinates" if random.random() < 0.5 and len(cells) <= 120 else "heights",
            "floor": random.choice(("bounded", "open")),
            "counts": counts,
            "num_cubes": len(cells),
        }
        return Entry(metadata=metadata, answer=",".join(map(str, counts)))

    def render_prompt(self, metadata):
        hs = metadata["heights"]
        width, depth = len(hs), len(hs[0])
        if metadata["floor"] == "bounded":
            floor = (f"The horizontal floor covers exactly the {width} by {depth} cells "
                     f"x=0..{width - 1}, y=0..{depth - 1}. It has no walls; faces "
                     "along its perimeter touch air.")
        else:
            floor = "The horizontal floor extends infinitely in both directions, with no walls."
        rule = ("All cubes are axis-aligned unit cubes. The floor is at z=0; cube (x,y,z) "
                "occupies [x,x+1] by [y,y+1] by [z,z+1]. A face is exposed exactly when "
                "it touches neither another cube nor the floor. Edge or corner contact "
                "does not hide a face. There are no cubes other than those specified.")
        if metadata["representation"] == "heights":
            grid = "\n".join(" ".join(map(str, row)) for row in hs)
            body = ("The height map has rows in increasing x and columns in increasing y, "
                    "both starting at 0. Height h means cubes at z=0 through h-1; "
                    f"0 means an empty column:\n{grid}")
        else:
            coords = ",".join(f"({x},{y},{z})" for x, y, z in metadata["coordinates"])
            body = f"The complete cube coordinate list (x, y, z) is:\n{coords}"
        question = ("Use neighbour counting to give how many cubes have exactly 0,1,2,3,4,5 "
                    "exposed faces, in that order, including fully hidden cubes. "
                    "Answer only c0,c1,c2,c3,c4,c5 with no spaces; for example a single "
                    "cube on the floor gives 0,0,0,0,0,1.")
        return f"A pile of cubes stands on a floor. {floor}\n{rule}\n{body}\n{question}"

    def score_answer(self, answer, entry):
        profile = _parse_profile(answer)
        return float(profile is not None and profile == _parse_profile(entry.answer))
