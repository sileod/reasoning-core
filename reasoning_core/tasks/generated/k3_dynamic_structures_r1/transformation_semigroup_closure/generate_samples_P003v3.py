import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.transformation_semigroup_closure.transformation_semigroup_closure import (
    TransformationSemigroupClosure,
)

random.seed(1259343118)


def main():
    out = Path(__file__).with_name("samples_P003v3.md")
    task = TransformationSemigroupClosure()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i + 1} (mode: {ex.metadata['mode']})")
            lines.append("Prompt:")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
