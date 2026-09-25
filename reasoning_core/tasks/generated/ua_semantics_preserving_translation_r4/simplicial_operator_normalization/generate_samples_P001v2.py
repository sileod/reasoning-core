import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.simplicial_operator_normalization.simplicial_operator_normalization import (
    SimplicialOperatorNormalization,
)

random.seed(2302342651)

OUT = Path(__file__).with_name("samples_P001v2.md")


def main():
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task = SimplicialOperatorNormalization()
        for i in range(2):
            ex = task.generate_example(level=level)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
