"""Z-order (Morton) index navigation over small power-of-two grids."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'morton_order_navigation (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_transfer_r1/morton_order_navigation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2639544549,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


@dataclass
class MortonNavigationConfig(Config):
    bits: int = 2

    def apply_difficulty(self, level):
        self.bits = 2 + level


def morton_encode(x, y, g):
    """Interleave the g low bits of row y and column x: x to even bits, y to odd."""
    index = 0
    for i in range(g):
        index |= ((x >> i) & 1) << (2 * i)
        index |= ((y >> i) & 1) << (2 * i + 1)
    return index


def morton_decode(index, g):
    """Split the 2g-bit Morton index back into column x and row y."""
    x = 0
    y = 0
    for i in range(g):
        x |= ((index >> (2 * i)) & 1) << i
        y |= ((index >> (2 * i + 1)) & 1) << i
    return x, y


def _morton_neighbor(x, y, g, direction):
    if direction == "east":
        return morton_encode(x + 1, y, g)
    if direction == "west":
        return morton_encode(x - 1, y, g)
    if direction == "north":
        return morton_encode(x, y - 1, g)
    if direction == "south":
        return morton_encode(x, y + 1, g)
    raise ValueError(direction)


DIRECTIONS = ("east", "west", "north", "south")


class MortonOrderNavigation(Task):
    summary = ("Interleave coordinate bits into Z-order (Morton) indices over small "
               "power-of-two grids: convert between cell coordinates and curve index, "
               "and answer the neighbor index of a queried cell.")
    config_cls = MortonNavigationConfig
    task_version = 2

    def generate_entry(self):
        g = self.config.bits
        n = 1 << g
        mode = random.choice(("enc", "dec", "neighbor"))
        if mode == "enc":
            x = random.randrange(n)
            y = random.randrange(n)
            index = morton_encode(x, y, g)
            metadata = {"mode": mode, "bits": g, "n": n, "x": x, "y": y}
            return Entry(metadata=metadata, answer=str(index))
        if mode == "dec":
            index = random.randrange(n * n)
            x, y = morton_decode(index, g)
            metadata = {"mode": mode, "bits": g, "n": n, "index": index}
            return Entry(metadata=metadata, answer="%d,%d" % (x, y))
        while True:
            direction = random.choice(DIRECTIONS)
            if direction == "east":
                x, y = random.randrange(n - 1), random.randrange(n)
            elif direction == "west":
                x, y = random.randrange(1, n), random.randrange(n)
            elif direction == "north":
                x, y = random.randrange(n), random.randrange(1, n)
            else:
                x, y = random.randrange(n), random.randrange(n - 1)
            index = _morton_neighbor(x, y, g, direction)
            assert 0 <= index < n * n
            break
        metadata = {"mode": mode, "bits": g, "n": n, "x": x, "y": y,
                    "direction": direction}
        return Entry(metadata=metadata, answer=str(index))

    def render_prompt(self, metadata):
        g = metadata["bits"]
        n = metadata["n"]
        mode = metadata["mode"]
        base = (
            "An %d-by-%d grid of cells is numbered in Z-order (Morton) curve index. "
            "For columns and rows numbered 0 to %d, index bit position 2i holds "
            "column bit i and position 2i+1 holds row bit i, for i from 0 to %d."
            % (n, n, n - 1, g - 1)
        )
        if mode == "enc":
            return (
                base + " What is the Morton (Z-order) index of the cell at column "
                "%d, row %d? Answer with a single integer." % (metadata["x"], metadata["y"])
            )
        if mode == "dec":
            return (
                base + " Which cell has Morton (Z-order) index %d? "
                "Answer as its column and row, written 'column,row'."
                % metadata["index"]
            )
        return (
            base + " The cell at column %d, row %d has a neighbor one cell to the %s "
            "(%s). What is the Morton (Z-order) index of that neighbor cell? "
            "Answer with a single integer."
            % (
                metadata["x"],
                metadata["y"],
                metadata["direction"],
                _direction_full(metadata["direction"]),
            )
        )


def _direction_full(direction):
    return {
        "east": "column increases by 1",
        "west": "column decreases by 1",
        "north": "row decreases by 1",
        "south": "row increases by 1",
    }[direction]
