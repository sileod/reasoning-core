import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.chip_firing_stabilization.chip_firing_stabilization import (
    ChipFiringStabilization,
)

random.seed(1139467751)


def main():
    task = ChipFiringStabilization()
    lines = []
    for level, label in ((0, "Level 0"), (2, "Level 2"), (5, "Level 5")):
        lines.append(f"## {label}")
        task.config.set_level(level)
        for i in range(2):
            x = task.generate_entry()
            prompt = task.render_prompt(x.metadata)
            lines.append(f"**Example {i + 1}**")
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {x.answer}")
            lines.append("")
    out = Path(__file__).with_name("samples_P007v1.md")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
