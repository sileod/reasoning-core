import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dependence_relevance_r1.simpson_reversal_detection.simpson_reversal_detection import (
    SimpsonReversalDetection,
)

random.seed(729651269)

OUT = Path(__file__).with_name("samples_P005v1.md")


def main():
    lines = []
    for level in (0, 2, 5):
        task = SimpsonReversalDetection()
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for idx in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {idx + 1}")
            lines.append("")
            lines.append("**Prompt**")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
