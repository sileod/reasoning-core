from pathlib import Path

import random

from reasoning_core.tasks.generated.ua_relational_structures_r5.contact_algebra_relations.contact_algebra_relations import (
    ContactAlgebraRelations,
)

OUT = Path(__file__).with_name("samples_P010v2.md")

random.seed(1211525277)

task = ContactAlgebraRelations()

lines = []
task_id = "contact_algebra_relations"

for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task.config.set_level(level)
    for i in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {i+1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(entry.prompt)
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(entry.answer)
        lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {OUT}")
