import random
from pathlib import Path

random.seed(1339177894)

from reasoning_core.tasks.generated.ua_relational_structures_r4.recursive_path_order_comparison.recursive_path_order_comparison import (
    RecursivePathOrderComparison,
)

task = RecursivePathOrderComparison()
lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append("# Level %d\n" % level)
    for i in range(2):
        x = task.generate_example()
        lines.append("## Example %d\n" % (i + 1))
        lines.append("### Prompt\n")
        lines.append("```\n" + x.prompt + "\n```\n")
        lines.append("### Answer\n")
        lines.append("```\n" + x.answer + "\n```\n")

out = Path(__file__).with_name("samples_P004v3.md")
out.write_text("\n".join(lines))
print("wrote", out)
