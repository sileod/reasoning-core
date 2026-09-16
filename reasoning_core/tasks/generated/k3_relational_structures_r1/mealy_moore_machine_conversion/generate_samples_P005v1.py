import random
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

random.seed(729651269)

from reasoning_core.tasks.generated.k3_relational_structures_r1.mealy_moore_machine_conversion.mealy_moore_machine_conversion import (  # noqa: E402
    MealyMooreMachineConversion,
)

out = Path(__file__).with_name("samples_P005v1.md")

lines = []
for level in (0, 2, 5):
    task = MealyMooreMachineConversion()
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for _ in range(2):
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        lines.append("**Prompt**")
        lines.append("")
        lines.append(prompt)
        lines.append("")
        lines.append("**Answer**")
        lines.append("")
        lines.append(x.answer)
        lines.append("")
        lines.append("---")
        lines.append("")

out.write_text("\n".join(lines))
print(out)
print("samples written")
