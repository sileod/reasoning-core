import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_compositional_generalization_r1.arc_consistency_reduction.arc_consistency_reduction import (
    ArcConsistencyReduction,
)

random.seed(1662004003)

task = ArcConsistencyReduction()

lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"# Level {level}")
    for idx in range(2):
        entry = task.generate_example()
        lines.append(f"## Example {idx + 1}")
        lines.append("**Prompt:**")
        lines.append(entry.metadata.get("_prompt", task.render_prompt(entry.metadata)))
        lines.append("")
        lines.append("**Answer:**")
        lines.append(entry.answer)
        lines.append("")

out = Path(__file__).with_name("samples_P001v1.md")
out.write_text("\n".join(lines), encoding="utf-8")
print(out)
