import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.contact_chain_displacement.contact_chain_displacement import (
    ContactChainDisplacement,
)

random.seed(2072234021)
task = ContactChainDisplacement()

out = Path(__file__).with_name("samples_P005v2.md")
lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    for _ in range(2):
        ex = task.generate_example(level=level)
        lines.append("### Prompt")
        lines.append(ex.prompt)
        lines.append("")
        lines.append(f"Answer: {ex.answer}")
        lines.append("")
out.write_text("\n".join(lines))
