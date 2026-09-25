import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.bitemporal_correction_slicing.bitemporal_correction_slicing import (
    BitemporalCorrectionSlicing,
)

random.seed(2409743872)

OUT = Path(__file__).with_name("samples_P010v1.md")

task = BitemporalCorrectionSlicing()
lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    for i in range(2):
        task.config.set_level(level)
        e = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("**Prompt**")
        lines.append(e.prompt)
        lines.append("")
        lines.append("**Answer**")
        lines.append(e.answer)
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT}")
