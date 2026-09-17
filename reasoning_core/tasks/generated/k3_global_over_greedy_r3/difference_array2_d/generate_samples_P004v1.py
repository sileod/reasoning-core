"""Generate samples_P004v1.md for the difference_array_2d task.

Two complete prompt/answer examples at each of levels 0, 2 and 5.
"""
import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_global_over_greedy_r3.difference_array_2d.difference_array_2d import (
    DifferenceArray2D,
)

SEED = 3536382515


def main():
    random.seed(SEED)
    task = DifferenceArray2D()
    out = ["# Difference array 2D samples (P004v1)\n"]
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for i in range(2):
            ex = task.generate_example()
            out.append(f"### Example {i + 1}\n")
            out.append(f"{ex.prompt}\n")
            out.append(f"**Answer**: {ex.answer}\n")
    text = "\n".join(out) + "\n"
    dest = Path(__file__).with_name("samples_P004v1.md")
    dest.write_text(text, encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
