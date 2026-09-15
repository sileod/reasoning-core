import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.convex_hull_ordering.convex_hull_ordering import (
    ConvexHullOrdering,
)

random.seed(2267388306)

task = ConvexHullOrdering()

levels = {0: 2, 2: 2, 5: 2}


def fmt_level(level, count):
    task.config.set_level(level)
    lines = [f"## Level {level}"]
    for i in range(count):
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(task.render_prompt(ex.metadata))
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(ex.answer)
        lines.append("")
    return "\n".join(lines)


sections = []
for level in [0, 2, 5]:
    sections.append(fmt_level(level, levels[level]))

out = Path(__file__).with_name("samples_P003v1.md")
out.write_text("\n".join(sections), encoding="utf-8")
print("wrote", out)
