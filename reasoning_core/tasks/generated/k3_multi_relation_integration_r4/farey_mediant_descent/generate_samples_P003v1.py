import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_multi_relation_integration_r4.farey_mediant_descent.farey_mediant_descent import (
    FareyMediantDescent,
)

random.seed(2267388306)

out = Path(__file__).with_name("samples_P003v1.md")
lines = []
task = FareyMediantDescent()
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    task.config = task.config_cls().set_level(level)
    for i in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(entry.prompt)
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(entry.answer)
        lines.append("")

out.write_text("\n".join(lines))
