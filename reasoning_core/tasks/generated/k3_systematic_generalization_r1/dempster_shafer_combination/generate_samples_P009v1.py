import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.dempster_shafer_combination.dempster_shafer_combination import (
    DempsterShaferCombination)

random.seed(3867019559)
OUT = Path(__file__).with_name("samples_P009v1.md")
TASK = DempsterShaferCombination()
TASK.seed = 3867019559
TASK.config.seed = 3867019559

lines = []
for level in (0, 2, 5):
    TASK.config.set_level(level)
    lines.append(f"\n## Level {level}\n")
    for i in range(2):
        e = TASK.generate_example()
        lines.append(f"### Example {i + 1}\n")
        lines.append(TASK.render_prompt(e.metadata))
        lines.append("\nAnswer:")
        lines.append(e.answer)
        lines.append("")

with open(OUT, "w") as fh:
    fh.write("\n".join(lines))
