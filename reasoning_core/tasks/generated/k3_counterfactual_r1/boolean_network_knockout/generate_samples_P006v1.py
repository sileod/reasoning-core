import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_counterfactual_r1.boolean_network_knockout.boolean_network_knockout import (
    BooleanNetworkKnockout,
)

seed = 798610012
random.seed(seed)

task = BooleanNetworkKnockout()

out_path = Path(__file__).with_name("samples_P006v1.md")


def run_level(level, n_examples=2):
    task.config.set_level(level)
    lines = []
    for i in range(n_examples):
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("**Prompt:**")
        lines.append("```")
        lines.append(task.render_prompt(ex.metadata))
        lines.append("```")
        lines.append("**Answer:**")
        lines.append("```")
        lines.append(ex.answer)
        lines.append("```")
        lines.append("")
    return lines


with open(out_path, "w") as f:
    for level in (0, 2, 5):
        f.write(f"# Level {level}\n\n")
        for line in run_level(level, 2):
            f.write(line + "\n")
        f.write("\n")
