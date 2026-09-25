import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.missingness_pattern_ignorability.missingness_pattern_ignorability import (
    MissingnessPatternIgnorability,
)

random.seed(682015719)

out = Path(__file__).with_name("samples_P008v1.md")
task = MissingnessPatternIgnorability()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    task.config.set_level(level)
    for i in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(task.render_prompt(entry.metadata))
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(entry.answer)
        lines.append("")

out.write_text("\n".join(lines))
