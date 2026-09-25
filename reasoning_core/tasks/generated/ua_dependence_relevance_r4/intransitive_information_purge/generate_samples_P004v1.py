"""Generate samples_P004v1.md for the intransitive_information_purge trial."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.intransitive_information_purge.intransitive_information_purge import (
    IntransitiveInformationPurge,
)

random.seed(3536382515)
OUT = Path(__file__).with_name("samples_P004v1.md")

task = IntransitiveInformationPurge()
lines = []
lines.append("# samples P004v1 — intransitive_information_purge")
lines.append("")
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for idx in range(2):
        e = task.generate_example()
        lines.append(f"### Example {idx + 1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append(f"**Answer:** {e.answer}")
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT}")
