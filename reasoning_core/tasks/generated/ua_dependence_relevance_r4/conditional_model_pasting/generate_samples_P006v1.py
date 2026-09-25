import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.conditional_model_pasting.conditional_model_pasting import (
    ConditionalModelPasting,
)

random.seed(798610012)

out = Path(__file__).with_name("samples_P006v1.md")
task = ConditionalModelPasting()

lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for _ in range(2):
        x = task.generate_example()
        lines.append("**Prompt:**")
        lines.append(task.render_prompt(x.metadata))
        lines.append("")
        lines.append("**Answer:**")
        lines.append(x.answer)
        lines.append("")

out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out)
