"""Generate samples_P002v1.md for levels 0, 2, 5."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.permutation_interval_inflation.permutation_interval_inflation import (
    PermutationIntervalInflation as P,
)

SEED = 1475571465
OUT = Path(__file__).with_name("samples_P002v1.md")


def main():
    random.seed(SEED)
    task = P()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(1, 3):
            ex = task.generate_example()
            lines.append(f"### Example {i} (level {level})")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append(f"**Answer:** {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
