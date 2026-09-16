import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.cayley_table_evaluation.cayley_table_evaluation import (
    CayleyTableEvaluation,
)

random.seed(2302342651)

LEVELS = (0, 2, 5)
PER_LEVEL = 2

out = Path(__file__).with_name("samples_P001v2.md")
lines = ["# CayleyTableEvaluation samples (P001v2)", ""]

task = CayleyTableEvaluation()
for level in LEVELS:
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for k in range(PER_LEVEL):
        x = task.generate_example()
        lines.append(f"### Example {k + 1}")
        lines.append("")
        lines.append(f"**Prompt:**")
        lines.append("")
        lines.append("```")
        lines.append(x.prompt)
        lines.append("```")
        lines.append("")
        lines.append(f"**Answer:** `{x.answer}`")
        lines.append("")

out.write_text("\n".join(lines) + "\n")
print(f"wrote {out}")
