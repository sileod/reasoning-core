import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.quadtree_region_construction.quadtree_region_construction import (
    QuadtreeRegionConstruction,
)

random.seed(729651269)

OUT = Path(__file__).with_name("samples_P005v1.md")


def main():
    lines = []
    task = QuadtreeRegionConstruction()
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        for _ in range(2):
            task.config.set_level(level)
            e = task.generate_example()
            prompt = task.render_prompt(e.metadata)
            lines.append(f"### Prompt\n```\n{prompt}\n```")
            lines.append(f"### Answer\n```\n{e.answer}\n```")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
