import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r4.savings_ordered_route_merging.savings_ordered_route_merging import (
    SavingsOrderedRouteMerging,
)

random.seed(2305351643)

task = SavingsOrderedRouteMerging()

lines = []
lines.append("# samples_P011v1")
lines.append("")

for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    task.config.set_level(level)
    for k in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {k + 1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append("```")
        lines.append(task.render_prompt(entry.metadata))
        lines.append("```")
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append("```")
        lines.append(entry.answer)
        lines.append("```")
        lines.append("")

out = Path(__file__).with_name("samples_P011v1.md")
out.write_text("\n".join(lines))
print("wrote", out)
