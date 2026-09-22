import random
from pathlib import Path

random.seed(729651269)

from reasoning_core.tasks.generated.k3_language_implementation_r4.representation_boundary_values.representation_boundary_values import (
    RepresentationBoundaryValues,
)


def main():
    task = RepresentationBoundaryValues()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(2):
            ex = task.generate_example()
            lines.append("### Prompt")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("### Answer")
            lines.append(ex.answer)
            lines.append("")
    out = Path(__file__).with_name("samples_P005v1.md")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
