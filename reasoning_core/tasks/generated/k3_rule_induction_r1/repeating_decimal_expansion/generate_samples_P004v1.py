import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_rule_induction_r1.repeating_decimal_expansion.repeating_decimal_expansion import (
    RepeatingDecimalExpansion,
)

random.seed(3536382515)

task = RepeatingDecimalExpansion()

lines = []
for level in (0, 2, 5):
    lines.append(f"Level {level}")
    task.config.set_level(level)
    for i in range(2):
        x = task.generate_example()
        lines.append("**Example prompt:**")
        lines.append(task.render_prompt(x.metadata))
        lines.append("**Answer:**")
        lines.append(x.answer)
        lines.append("")

out = Path(__file__).with_name("samples_P004v1.md")
out.write_text("\n".join(lines) + "\n")
