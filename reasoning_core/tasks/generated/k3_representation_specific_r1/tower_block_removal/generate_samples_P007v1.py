import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_specific_r1.tower_block_removal.tower_block_removal import (
    TowerBlockRemoval,
)

random.seed(1139467751)

OUT = Path(__file__).with_name("samples_P007v1.md")


def main():
    task = TowerBlockRemoval()
    blocks = []
    for level in (0, 2, 5):
        blocks.append(f"## Level {level}\n")
        for _ in range(2):
            entry = task.generate_example(level=level)
            blocks.append("### Prompt\n")
            blocks.append(entry.prompt)
            blocks.append("\n")
            blocks.append("**Answer:** " + entry.answer)
            blocks.append("\n")
    OUT.write_text("\n".join(blocks) + "\n")


if __name__ == "__main__":
    main()
