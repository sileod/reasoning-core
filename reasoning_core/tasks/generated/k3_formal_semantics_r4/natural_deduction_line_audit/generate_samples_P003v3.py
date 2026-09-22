import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_semantics_r4.natural_deduction_line_audit.natural_deduction_line_audit import (
    NaturalDeductionLineAudit,
)

random.seed(1259343118)

task = NaturalDeductionLineAudit()

out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append("# Level %d\n" % level)
    for i in range(2):
        ex = task.generate_example()
        out.append("## Example %d\n" % (i + 1))
        out.append("**Prompt:**\n")
        out.append(task.render_prompt(ex.metadata) + "\n")
        out.append("**Answer:**\n")
        out.append(ex.answer + "\n")
    out.append("\n")

Path(__file__).with_name("samples_P003v3.md").write_text("\n".join(out))
print("written")
