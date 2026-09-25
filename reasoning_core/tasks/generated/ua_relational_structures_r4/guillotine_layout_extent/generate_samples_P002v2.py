import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_relational_structures_r4.guillotine_layout_extent.guillotine_layout_extent import (  # noqa
    GuillotineLayoutExtent,
)

random.seed(1336314872)

task = GuillotineLayoutExtent()

_LABELS = {0: "Level 0", 2: "Level 2", 5: "Level 5"}

lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## {_LABELS[level]}")
    for _ in range(2):
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        lines.append("### Example")
        lines.append("**Prompt**")
        lines.append("```text")
        lines.append(prompt)
        lines.append("```")
        lines.append("**Answer**")
        lines.append("```text")
        lines.append(x.answer)
        lines.append("```")
        lines.append("")

out = Path(__file__).with_name("samples_P002v2.md")
out.write_text("\n".join(lines))
print("wrote", out)
