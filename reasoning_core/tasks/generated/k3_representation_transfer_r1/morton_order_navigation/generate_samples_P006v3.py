"""Generate the samples file for trial P006v3 (Morton order navigation)."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_transfer_r1.morton_order_navigation.morton_order_navigation import (
    MortonOrderNavigation,
)

SEED = 2639544549
LEVELS = (0, 2, 5)
PER_LEVEL = 2


def main():
    random.seed(SEED)
    out = []
    task = MortonOrderNavigation()
    for level in LEVELS:
        out.append("Level %d" % level)
        task.config.set_level(level)
        for _ in range(PER_LEVEL):
            entry = task.generate_example(level=level)
            out.append("Prompt: " + entry.prompt)
            out.append("Answer: " + entry.answer)
            out.append("")
    out.append("")
    text = "\n".join(out)
    target = Path(__file__).with_name("samples_P006v3.md")
    target.write_text(text)


if __name__ == "__main__":
    main()
