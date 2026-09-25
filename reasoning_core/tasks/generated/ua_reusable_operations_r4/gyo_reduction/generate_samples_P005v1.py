import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_reusable_operations_r4.hypergraph_gyo_reduction.hypergraph_gyo_reduction import (
    GyoReduction,
)

random.seed(729651269)

OUT = Path(__file__).with_name("samples_P005v1.md")

task = GyoReduction()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task.config.set_level(level)
    for _ in range(2):
        x = task.generate_example()
        lines.append(task.render_prompt(x.metadata))
        lines.append("")
        lines.append("Answer: %s" % x.answer)
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
