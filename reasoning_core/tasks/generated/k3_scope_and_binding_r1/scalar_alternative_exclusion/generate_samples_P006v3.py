import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.scalar_alternative_exclusion.scalar_alternative_exclusion import (
    ScalarAlternativeExclusion,
)

OUT = Path(__file__).with_name("samples_P006v3.md")
SEED = 2639544549


def main():
    random.seed(SEED)
    task = ScalarAlternativeExclusion()
    lines = ["# scalar_alternative_exclusion samples", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for idx in range(2):
            entry = task.generate_example(level=level)
            lines.append(f"**Example {idx + 1}**")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(entry.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
