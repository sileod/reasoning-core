import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_rule_induction_r1.functional_graph_cycle_finding.functional_graph_cycle_finding import (
    CycleFinder,
)

random.seed(729651269)

LEVELS = [0, 2, 5]

lines = ["# Samples for P005v1 functional_graph_cycle_finding", ""]
task = CycleFinder()

for level in LEVELS:
    lines.append("## Level {}".format(level))
    lines.append("")
    task.config.set_level(level)
    for _ in range(2):
        entry = task.generate_example()
        lines.append("### Prompt")
        lines.append("")
        lines.append(task.render_prompt(entry.metadata))
        lines.append("")
        lines.append("### Answer")
        lines.append("")
        lines.append(entry.answer)
        lines.append("")

out = Path(__file__).with_name("samples_P005v1.md")
out.write_text("\n".join(lines))
print("wrote", out)
