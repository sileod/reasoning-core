import random
import sys
from pathlib import Path

from reasoning_core.tasks.generated.k3_state_tracking_r4.ferrers_diagram_operations.ferrers_diagram_operations import (
    FerrersDiagramOperations,
)

OUT = Path(__file__).with_name("samples_P003v1.md")


def main():
    random.seed(2267388306)
    task = FerrersDiagramOperations()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        task.config.set_level(level)
        for k in range(2):
            e = task.generate_entry()
            lines.append(f"## Example {k+1}")
            lines.append("")
            lines.append(task.render_prompt(e.metadata))
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
