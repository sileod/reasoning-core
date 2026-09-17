"""Seeded sample generation for P006v3 (byte-reproducible)."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_specific_r2.backdoor_adjustment_selection.backdoor_adjustment_selection import (
    BackdoorAdjustmentSelection,
)


def main():
    random.seed(2639544549)
    task = BackdoorAdjustmentSelection()
    out = Path(__file__).with_name("samples_P006v3.md")
    lines = ["# Samples: backdoor_adjustment_selection (P006v3)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(2):
            entry = task.generate_entry()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
