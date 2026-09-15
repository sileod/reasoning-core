import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.linearizability_check.linearizability_check import (
    LinearizabilityCheck,
)

random.seed(3622015929)

out = Path(__file__).with_name("samples_P007v1.md")

task = LinearizabilityCheck()
lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for _ in range(2):
        e = task.generate_example()
        lines.append(f"### Prompt")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append(f"**Answer**: {e.answer}")
        lines.append("")

out.write_text("\n".join(lines))
print("wrote", out)
