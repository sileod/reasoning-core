import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_specific_r1.matrix_jordan_normal_form.matrix_jordan_normal_form import (
    MatrixJordan,
    MatrixJordanConfig,
)

random.seed(3536382515)


def main():
    out = Path(__file__).with_name("samples_P004v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        cfg = MatrixJordanConfig()
        cfg.set_level(level)
        task = MatrixJordan()
        task.config = cfg
        for i in range(2):
            entry = task.generate_entry()
            lines.append(f"### Example {i + 1}")
            lines.append("**Prompt:**")
            lines.append("```")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("```")
            lines.append("**Answer:**")
            lines.append("```")
            lines.append(entry.answer)
            lines.append("```")
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
