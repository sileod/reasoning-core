import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.iterated_integral_shuffle_expansion.iterated_integral_shuffle_expansion import (
    IteratedIntegralShuffleExpansion,
)

random.seed(1277236794)

task = IteratedIntegralShuffleExpansion()

level_groups = {0: "Level 0", 2: "Level 2", 5: "Level 5"}

lines = []
for level in [0, 2, 5]:
    task.config.set_level(level)
    lines.append(f"## {level_groups[level]}")
    for ex in range(1, 3):
        e = task.generate_example()
        lines.append(f"**Example {ex}**")
        lines.append("Prompt:")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append("Answer:")
        lines.append(e.answer)
        lines.append("")

Path(__file__).with_name("samples_P012v1.md").write_text("\n".join(lines))
