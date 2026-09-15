import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relevance_separation_r1.sensitive_input_identification.sensitive_input_identification import (
    SensitiveInputIdentification,
)

random.seed(729651269)

task = SensitiveInputIdentification()

out_path = Path(__file__).with_name("samples_P005v1.md")


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
