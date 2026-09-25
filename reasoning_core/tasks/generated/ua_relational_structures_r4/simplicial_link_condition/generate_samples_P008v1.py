import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_relational_structures_r4.simplicial_link_condition.simplicial_link_condition import (
    SimplicialLinkCondition,
)

random.seed(682015719)

task = SimplicialLinkCondition()
out = []
for level in (0, 2, 5):
    out.append(f"## Level {level}")
    out.append("")
    for _ in range(2):
        ex = task.generate_example(level=level)
        out.append("Prompt:")
        out.append("")
        out.append(ex.prompt)
        out.append("")
        out.append("Answer:")
        out.append("")
        out.append(ex.answer)
        out.append("")

Path(__file__).with_name("samples_P008v1.md").write_text("\n".join(out) + "\n")
