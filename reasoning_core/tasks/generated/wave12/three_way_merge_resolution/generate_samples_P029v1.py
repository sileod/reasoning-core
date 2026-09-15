import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.three_way_merge_resolution.three_way_merge_resolution import (
    ThreeWayMergeResolution,
)

random.seed(1602009423)

task = ThreeWayMergeResolution()
out = Path(__file__).with_name("samples_P029v1.md")
lines = ["# Samples P029v1 - three_way_merge_resolution", ""]

for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    cfg = ThreeWayMergeResolution.Config if hasattr(ThreeWayMergeResolution, "Config") else None
    task.config.set_level(level)
    for i in range(2):
        e = task.generate_example()
        lines.append(f"### Example {i+1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(e.answer)
        lines.append("")
        lines.append("")

out.write_text("\n".join(lines))
print("wrote", out)
