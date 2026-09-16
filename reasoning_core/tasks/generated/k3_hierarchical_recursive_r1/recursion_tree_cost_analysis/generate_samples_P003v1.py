import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.recursion_tree_cost_analysis.recursion_tree_cost_analysis import (
    RecursionTreeCostAnalysis,
)

random.seed(2267388306)

out = Path(__file__).with_name("samples_P003v1.md")
lines = []
lines.append("# Samples for P003v1\n")

for level in (0, 2, 5):
    lines.append(f"## Level {level}\n")
    config = RecursionTreeCostAnalysis.config_cls()
    config.set_level(level)
    task = RecursionTreeCostAnalysis(config=config)
    for i in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append(f"### Example {i+1}\n")
        lines.append(f"**Prompt:**\n\n{prompt}\n")
        lines.append(f"**Answer:** {ex.answer}\n")
    lines.append("")

out.write_text("\n".join(lines))
print(out)
