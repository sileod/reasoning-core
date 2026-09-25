import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r5.simplest_surreal_separator.simplest_surreal_separator import (
    SimplestSurrealSeparator,
)

random.seed(3867019559)

out = Path(__file__).with_name("samples_P009v1.md")
task = SimplestSurrealSeparator()
lines = []
for level in (0, 2, 5):
    lines.append(f"# Level {level}")
    task.config.set_level(level)
    for i in range(2):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        lines.append(f"## Example {i + 1}")
        lines.append(f"**Prompt:** {prompt}")
        lines.append("")
        lines.append(f"**Answer:** {entry.answer}")
        lines.append("")

out.write_text("\n".join(lines))
