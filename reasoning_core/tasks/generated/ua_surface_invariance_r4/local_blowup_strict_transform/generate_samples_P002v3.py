import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_surface_invariance_r4.local_blowup_strict_transform.local_blowup_strict_transform import (
    LocalBlowupStrictTransform,
)

random.seed(368817805)

OUT = Path(__file__).with_name("samples_P002v3.md")

task = LocalBlowupStrictTransform()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    task.config.set_level(level)
    for _ in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append("**Example**")
        lines.append("")
        lines.append("```")
        lines.append(prompt)
        lines.append("```")
        lines.append("")
        lines.append("**Answer**")
        lines.append("")
        lines.append(f"`{ex.answer}`")
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT}")
