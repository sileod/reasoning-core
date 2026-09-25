import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_relational_structures_r4.hydra_cut_regrowth.hydra_cut_regrowth import (
    HydraCutRegrowth,
)

random.seed(382564971)

LEVELS = [0, 2, 5]
PER_LEVEL = 2

lines = []
for level in LEVELS:
    task = HydraCutRegrowth()
    task.config.set_level(level)
    lines.append(f"# Level {level}")
    lines.append("")
    for i in range(PER_LEVEL):
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        lines.append(f"## Example {i + 1}")
        lines.append("")
        lines.append("Prompt:")
        lines.append("")
        lines.append(prompt)
        lines.append("")
        lines.append(f"Answer: {x.answer}")
        lines.append("")

Path(__file__).with_name("samples_P003v2.md").write_text("\n".join(lines))
