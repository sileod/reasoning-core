import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_transfer_r1.critical_pair_generation.critical_pair_generation import (
    CriticalPairGeneration,
)

random.seed(1139467751)

out = Path(__file__).with_name("samples_P007v1.md")
task = CriticalPairGeneration()
lines = ["# Samples P007v1\n"]

for lvl in [0, 2, 5]:
    lines.append(f"## Level {lvl}\n")
    task.config.set_level(lvl)
    for i in range(2):
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}\n")
        lines.append("Prompt:\n")
        lines.append(task.render_prompt(ex.metadata) + "\n")
        lines.append("Answer:\n")
        lines.append(ex.answer + "\n")

out.write_text("\n".join(lines))
print(out)
