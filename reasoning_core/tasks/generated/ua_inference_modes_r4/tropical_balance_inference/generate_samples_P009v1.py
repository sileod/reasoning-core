import random
from pathlib import Path

random.seed(3867019559)

from reasoning_core.tasks.generated.ua_inference_modes_r4.tropical_balance_inference.tropical_balance_inference import (
    TropicalBalanceInference,
)

task = TropicalBalanceInference()
out = Path(__file__).with_name("samples_P009v1.md")

lines = []
lines.append("# tropical_balance_inference - samples (P009v1)")
lines.append("")
lines.append("Seed: 3867019559")
lines.append("")

for level in (0, 2, 5):
    lines.append("## Level %d" % level)
    lines.append("")
    for i in range(2):
        ex = task.generate_example(level=level)
        lines.append("### Example %d" % (i + 1))
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(ex.prompt)
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(ex.answer)
        lines.append("")

out.write_text("\n".join(lines))
print("wrote", out)
