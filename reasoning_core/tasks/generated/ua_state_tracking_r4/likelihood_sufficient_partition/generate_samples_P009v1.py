import random
from pathlib import Path

random.seed(3867019559)

from reasoning_core.tasks.generated.ua_state_tracking_r4.likelihood_sufficient_partition.likelihood_sufficient_partition import (
    LikelihoodSufficientPartition,
)

task = LikelihoodSufficientPartition()
out = Path(__file__).resolve().with_name("samples_P009v1.md")
lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}\n")
    for idx in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {idx + 1}\n")
        lines.append("**Prompt:**\n")
        lines.append(task.render_prompt(entry.metadata))
        lines.append("\n**Answer:**\n")
        lines.append(entry.answer)
        lines.append("\n")
out.write_text("\n".join(lines))
print(f"wrote {out}")
