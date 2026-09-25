"""Generate the samples_P001v1.md file for the mechanical backlash induction trial."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_rule_induction_r4.mechanical_backlash_induction.mechanical_backlash_induction import (
    MechanicalBacklashInduction,
)

seed = 1662004003
out = Path(__file__).with_name("samples_P001v1.md")


def emit():
    random.seed(seed)
    task = MechanicalBacklashInduction()
    lines = ["# Mechanical backlash induction - samples (P001v1)", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    out.write_text(emit())
    print(f"wrote {out}")
