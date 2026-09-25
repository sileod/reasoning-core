import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_latent_structure_reconstruction_r4.sandpile_recurrence_membership.task_sandpile_recurrence_membership import (
    SandpileRecurrenceMembership,
)

random.seed(1336314872)

OUT = Path(__file__).with_name("samples_P002v2.md")

task = SandpileRecurrenceMembership()

lines = []
for level in (0, 2, 5):
    lines.append(f"# Level {level}")
    lines.append("")
    task.config.set_level(level)
    for _ in range(2):
        entry = task.generate_example()
        lines.append("Prompt:")
        lines.append(task.render_prompt(entry.metadata))
        lines.append("")
        lines.append(f"Answer: {entry.answer}")
        lines.append("")

OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
