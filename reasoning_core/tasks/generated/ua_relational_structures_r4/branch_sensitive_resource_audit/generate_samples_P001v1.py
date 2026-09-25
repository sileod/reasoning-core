import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_relational_structures_r4.branch_sensitive_resource_audit.branch_sensitive_resource_audit import (
    BranchSensitiveResourceAudit,
)

random.seed(1662004003)

OUT = Path(__file__).with_name("samples_P001v1.md")

task = BranchSensitiveResourceAudit()

lines = []
for level in (0, 2, 5):
    lines.append("## Level %d" % level)
    for i in range(2):
        ex = task.generate_example(level=level)
        lines.append("### Example %d" % (i + 1))
        lines.append("**Prompt:**")
        lines.append("```")
        lines.append(ex.prompt)
        lines.append("```")
        lines.append("**Answer:**")
        lines.append("```")
        lines.append(ex.answer)
        lines.append("```")
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
