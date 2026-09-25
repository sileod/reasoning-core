import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_specific_r4.set_family_shattering.set_family_shattering import (
    SetFamilyShattering,
)

random.seed(729651269)

task = SetFamilyShattering()

lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for _ in range(2):
        x = task.generate_example()
        lines.append("Prompt:")
        lines.append("```")
        lines.append(task.render_prompt(x.metadata))
        lines.append("```")
        lines.append("Answer:")
        lines.append("```")
        lines.append(x.answer)
        lines.append("```")
        lines.append("")
    lines.append("")

out = Path(__file__).with_name("samples_P005v1.md")
out.write_text("\n".join(lines))
print("wrote", out)
