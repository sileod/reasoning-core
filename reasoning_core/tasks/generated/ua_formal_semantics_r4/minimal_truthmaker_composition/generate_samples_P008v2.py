import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_semantics_r4.minimal_truthmaker_composition import (
    minimal_truthmaker_composition as m,
)

SEED = 3020341981
OUT = Path(__file__).with_name("samples_P008v2.md")

task = m.MinimalTruthmakerComposition()

lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for i in range(2):
        random.seed(SEED + level * 100 + i)
        x = task.generate_example()
        lines.append(f"### Example {i+1}")
        lines.append(task.render_prompt(x.metadata))
        lines.append("")
        lines.append(f"**Answer:** {x.answer}")
        lines.append("")

OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
