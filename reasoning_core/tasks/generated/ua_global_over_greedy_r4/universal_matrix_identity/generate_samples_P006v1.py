import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.universal_matrix_identity.universal_matrix_identity import (
    UniversalMatrixIdentity,
)


def main():
    random.seed(798610012)
    task = UniversalMatrixIdentity()
    out = Path(__file__).with_name("samples_P006v1.md")
    levels = (0, 2, 5)
    lines = []
    for level in levels:
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example(level=level)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
