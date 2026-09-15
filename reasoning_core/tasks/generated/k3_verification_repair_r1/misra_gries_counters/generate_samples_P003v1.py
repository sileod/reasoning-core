import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_verification_repair_r1.misra_gries_counters.misra_gries_counters import (
    MisraGriesCounters,
)

random.seed(2267388306)

OUT = Path(__file__).with_name("samples_P003v1.md")

task = MisraGriesCounters()

lines = []
for label, level in (("Level 0", 0), ("Level 2", 2), ("Level 5", 5)):
    lines.append(f"# {label}")
    task.config.set_level(level)
    for i in range(1, 3):
        e = task.generate_entry()
        prompt = task.render_prompt(e.metadata)
        lines.append(f"## Example {i}")
        lines.append("Prompt:")
        lines.append(prompt)
        lines.append("Answer:")
        lines.append(e.answer)
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT}")
