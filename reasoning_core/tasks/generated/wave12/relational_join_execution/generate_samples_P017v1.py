import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.relational_join_execution.relational_join_execution import (
    RelationalJoinExecution,
)

random.seed(1718001595)

task = RelationalJoinExecution()

out = []

for level in (0, 2, 5):
    out.append(f"## Level {level}")
    out.append("")
    for _ in range(2):
        ex = task.generate_example(level=level)
        out.append("### Prompt")
        out.append("")
        out.append(ex.prompt)
        out.append("")
        out.append("### Answer")
        out.append("")
        out.append(ex.answer)
        out.append("")
        out.append("---")
        out.append("")

(Path(__file__).with_name("samples_P017v1.md")).write_text("\n".join(out), encoding="utf-8")
print("wrote", Path(__file__).with_name("samples_P017v1.md"))
