import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_psychometrics_r5.polarization_projection_cascade.polarization_projection_cascade import (
    PolarizationProjectionCascade,
)

OUT = Path(__file__).with_name("samples_P008v1.md")


def main():
    task = PolarizationProjectionCascade()
    parts = []
    for level in (0, 2, 5):
        parts.append(f"## Level {level}")
        for k in range(2):
            ex = task.generate_example(level=level)
            parts.append(f"### Example {k + 1}")
            parts.append("**Prompt:**")
            parts.append("```")
            parts.append(ex.prompt)
            parts.append("```")
            parts.append("**Answer:**")
            parts.append("```")
            parts.append(ex.answer)
            parts.append("```")
    OUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    random.seed(682015719)
    main()
