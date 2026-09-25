import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_specific_r4.partition_rim_strip_cancellation.partition_rim_strip_cancellation import (
    PartitionRimStripCancellation,
)

random.seed(241712510)

task = PartitionRimStripCancellation()
out = Path(__file__).with_name("samples_P007v2.md")
lines = []

for lvl in (0, 2, 5):
    task.config.set_level(lvl)
    lines.append(f"## Level {lvl}")
    lines.append("")
    for i in range(2):
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("**Prompt:**")
        lines.append(ex.prompt)
        lines.append("")
        lines.append("**Answer:**")
        lines.append(ex.answer)
        lines.append("")

out.write_text("\n".join(lines))
