import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.rounded_display_consistency.rounded_display_consistency import (
    RoundedDisplayConsistency,
)

random.seed(3020341981)

OUT = Path(__file__).with_name("samples_P008v2.md")

LEVELS = (0, 2, 5)
EXAMPLES_PER_LEVEL = 2
sample_count = 2

task = RoundedDisplayConsistency()

lines = []
for level in LEVELS:
    task.config.set_level(level)
    lines.append("## Level %d" % level)
    lines.append("")
    for i in range(EXAMPLES_PER_LEVEL):
        e = task.generate_example()
        lines.append("Prompt %d:" % (i + 1))
        lines.append("")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append("Answer: %s" % e.answer)
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
