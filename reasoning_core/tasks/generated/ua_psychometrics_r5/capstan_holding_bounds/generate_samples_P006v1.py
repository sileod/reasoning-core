import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_psychometrics_r5.capstan_holding_bounds.capstan_holding_bounds import (
    CapstanHoldingBounds,
)

random.seed(798610012)

LEVELS = [0, 2, 5]
PER_LEVEL = 2

out = Path(__file__).with_name("samples_P006v1.md")
lines = ["# Samples for capstan_holding_bounds", ""]

task = CapstanHoldingBounds()

for level in LEVELS:
    lines.append(f"## Level {level}")
    lines.append("")
    cfg = task.config_cls()
    cfg.set_level(level)
    task.config = cfg
    for i in range(PER_LEVEL):
        entry = task.generate_entry()
        lines.append(f"### Example {i+1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append("```")
        lines.append(task.render_prompt(entry.metadata))
        lines.append("```")
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(entry.answer)
        lines.append("")

out.write_text("\n".join(lines))
print("wrote", out)
