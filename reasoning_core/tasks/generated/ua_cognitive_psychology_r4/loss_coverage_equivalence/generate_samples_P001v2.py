"""Generate samples_P001v2.md for the loss_coverage_equivalence trial.

Seeded for byte-reproducible output. Prints two complete prompt/answer examples
at levels 0, 2 and 5, verbatim.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.loss_coverage_equivalence.loss_coverage_equivalence import (
    LossCoverageEquivalence,
)

SEED = 2302342651
OUT = Path(__file__).with_name("samples_P001v2.md")


def main():
    random.seed(SEED)
    task = LossCoverageEquivalence()
    lines = ["# samples_P001v2", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for k in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {k + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
