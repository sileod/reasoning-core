import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SteppedSurfaceConfig(Config):
    size: int = 2
    maxh: int = 2

    def apply_difficulty(self, level):
        self.size = 2 + level
        self.maxh = 2 + level


def make_plane_partition(size, maxh):
    """A weakly row/column monotone height array (plane partition / stepped surface)."""
    h = [[0] * size for _ in range(size)]
    h[0][0] = random.randint(0, maxh)
    for j in range(1, size):
        h[0][j] = random.randint(0, h[0][j - 1])
    for i in range(1, size):
        h[i][0] = random.randint(0, h[i - 1][0])
    for i in range(1, size):
        for j in range(1, size):
            h[i][j] = random.randint(0, min(h[i - 1][j], h[i][j - 1]))
    return h


def _height_answer(entry):
    return str(entry.metadata["step"])


def _cube_answer(entry):
    return "yes" if entry.metadata["occupied"] else "no"


def _cross_answer(meta):
    return "".join(
        "X" if meta["height"][r][c] >= meta["level"] else "."
        for r in range(len(meta["height"]))
        for c in range(len(meta["height"][0]))
    )


def score_height(answer, entry):
    try:
        return 1.0 if int(str(answer).strip()) == int(entry.metadata["step"]) else 0.0
    except (TypeError, ValueError):
        return 0.0


def score_cube(answer, entry):
    a = str(answer).strip().lower()
    return 1.0 if a == entry.metadata["answer"] else 0.0


def score_cross(answer, entry):
    a = str(answer).strip()
    return 1.0 if a == _cross_answer(entry.metadata) else 0.0


class SteppedSurfaceReconstruction(Task):
    summary = ("Return a queried column height, a cube-occupancy flag, or a row-major "
               "cross-section symbol string of a stepped surface given as a monotone height "
               "array, mapping the array across the equivalent cube order ideal and lozenge "
               "height-function views.")
    design_choice = ("Answer form varies: for a given query, output a single integer height, "
                     "a binary occupied flag, or a short string of cross-section symbols, "
                     "with the query type fixed per instance.")
    config_cls = SteppedSurfaceConfig
    task_version = 2

    def generate_entry(self):
        size, maxh = self.config.size, self.config.maxh
        h = make_plane_partition(size, maxh)
        qt = random.choice(("height", "cube", "cross"))
        if qt == "height":
            r = random.randrange(size)
            c = random.randrange(size)
            answer = str(h[r][c])
            metadata = {
                "query": "height",
                "height": [list(row) for row in h],
                "r": r,
                "c": c,
                "step": h[r][c],
            }
        elif qt == "cube":
            r = random.randrange(size)
            c = random.randrange(size)
            occupied = random.random() < 0.5
            k = h[r][c] if occupied else h[r][c] + 1
            metadata = {
                "query": "cube",
                "height": [list(row) for row in h],
                "r": r,
                "c": c,
                "k": k,
                "occupied": occupied,
                "answer": "yes" if occupied else "no",
            }
            answer = "yes" if occupied else "no"
        else:
            level = random.randint(1, maxh)
            metadata = {
                "query": "cross",
                "height": [list(row) for row in h],
                "level": level,
            }
            answer = _cross_answer(metadata)
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        size = len(metadata["height"])
        grid = "\n".join(
            " ".join(str(v) for v in row) for row in metadata["height"]
        )
        header = (
            f"A stepped surface over a {size}x{size} box is given by a monotone height "
            f"array H: column (r,c) stacks H[r][c] unit cubes, so H is the top face of a "
            f"3D order ideal of cubes and the height function of the equivalent lozenge "
            f"tiling. H never increases as r or c grows. Rows are indexed 0..{size - 1} "
            f"top to bottom, columns 0..{size - 1} left to right.\n\n"
            f"Height array:\n{grid}\n\n"
        )
        q = metadata["query"]
        if q == "height":
            return header + (
                f"What is the cube-stack height at column ({metadata['r']},{metadata['c']}) "
                f"on this surface? Give the answer as a single number."
            )
        if q == "cube":
            return header + (
                f"A unit cube (r,c,k) is inside the order ideal exactly when k <= H[r][c]. "
                f"Is the cube ({metadata['r']},{metadata['c']},{metadata['k']}) occupied? "
                f"Give the answer as a single word."
            )
        return header + (
            f"At integer level k, the cross-section marks each column (r,c) occupied when "
            f"H[r][c] >= k. Give the cross-section at level {metadata['level']} as one "
            f"string of length {size * size}, reading rows in order and within each row "
            f"columns in order, writing X for an occupied column and . for an empty one. "
            f"Give the answer as a single string."
        )

    def score_answer(self, answer, entry):
        q = entry.metadata["query"]
        if q == "height":
            return score_height(answer, entry)
        if q == "cube":
            return score_cube(answer, entry)
        return score_cross(answer, entry)


TASK_META = {'parent_source_id': None,
 'idea': 'stepped_surface_reconstruction (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_transfer_r4/stepped_surface_reconstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
