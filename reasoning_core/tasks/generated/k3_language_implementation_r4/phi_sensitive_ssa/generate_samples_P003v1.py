import random
from pathlib import Path

random.seed(2267388306)

from reasoning_core.tasks.generated.k3_language_implementation_r4.phi_sensitive_ssa_evaluation.phi_sensitive_ssa import (
    PhiSensitiveSSA,
)

out = Path(__file__).with_name("samples_P003v1.md")
task = PhiSensitiveSSA()
levels = [0, 2, 5]
lines = []
for lvl in levels:
    lines.append("")
    lines.append("## Level %d" % lvl)
    lines.append("")
    for _ in range(2):
        e = task.generate_example(level=lvl)
        lines.append("### Prompt")
        lines.append("")
        lines.append("```")
        lines.append(task.render_prompt(e.metadata))
        lines.append("```")
        lines.append("")
        lines.append("### Answer")
        lines.append("")
        lines.append("```")
        lines.append(str(e.answer))
        lines.append("```")
        lines.append("")

out.write_text("\n".join(lines) + "\n")
print("wrote", out)
