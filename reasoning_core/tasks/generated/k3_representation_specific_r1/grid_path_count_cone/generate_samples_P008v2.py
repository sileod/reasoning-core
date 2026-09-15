import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_specific_r1.grid_path_count_cone.grid_path_count_cone import (
    GridPathCountCone,
)

random.seed(3020341981)


def main():
    task = GridPathCountCone()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for _ in range(2):
            ex = task.generate_example()
            lines.append("### Prompt")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("### Answer")
            lines.append(ex.answer)
            lines.append("")
    out = Path(__file__).with_name("samples_P008v2.md")
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
