"""Generate samples_P007v1.md for the sequential_boundary_crossing trial."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.sequential_boundary_crossing import (
    sequential_boundary_crossing as mod,
)

SEED = 1139467751
OUT = Path(__file__).with_name("samples_P007v1.md")


def main():
    random.seed(SEED)
    task = mod.SequentialBoundaryCrossing()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        for _ in range(2):
            task.config.set_level(level)
            x = task.generate_example()
            lines.append("### Prompt")
            lines.append(task.render_prompt(x.metadata))
            lines.append("### Answer")
            lines.append(x.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
