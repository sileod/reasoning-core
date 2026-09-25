"""Generate samples_P002v1.md for differential_shaft_propagation at levels 0, 2, 5."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_relevance_separation_r5.differential_shaft_propagation.differential_shaft_propagation import (  # noqa: E501
    DifferentialShaftPropagation,
)

SEED = 1475571465
OUT = Path(__file__).with_name("samples_P002v1.md")


def main():
    random.seed(SEED)
    task = DifferentialShaftPropagation()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(2):
            entry = task.generate_example()
            lines.append("")
            lines.append("**Prompt:**")
            lines.append(entry.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
