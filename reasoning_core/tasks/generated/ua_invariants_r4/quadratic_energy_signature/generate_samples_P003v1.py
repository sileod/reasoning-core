"""Generate samples_P003v1.md for quadratic_energy_signature."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_invariants_r4.quadratic_energy_signature.quadratic_energy_signature import (
    QuadraticEnergySignature,
)

random.seed(2267388306)

OUT = Path(__file__).with_name("samples_P003v1.md")
task = QuadraticEnergySignature()

lines = []
lines.append("# P003v1 samples: quadratic_energy_signature")
lines.append("")

for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for i in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {i + 1}")
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
print("wrote", OUT)
