import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.decision_tree_induction import (
    decision_tree_induction as module,
)

random.seed(798610012)

task = module.DecisionTreeInduction()

out_path = Path(__file__).with_name("samples_P006v1.md")

lines = []
for level in (0, 2, 5):
    lines.append("\n## Level {}".format(level))
    task.config.set_level(level)
    for i in range(2):
        x = task.generate_example()
        lines.append("\n### Example {}".format(i + 1))
        lines.append("\n**Prompt:**")
        lines.append("")
        lines.append("```")
        lines.append(module.module_render_prompt(x.metadata))
        lines.append("```")
        lines.append("\n**Answer:**")
        lines.append("")
        lines.append("```")
        lines.append(x.answer)
        lines.append("```")

samples = "# P006v1 Samples\n\n" + "\n".join(lines) + "\n"
out_path.write_text(samples)
print("wrote", out_path)
