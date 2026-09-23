import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.comparator_network_zero_one_verification.comparator_network_zero_one_verification import (
    ComparatorZeroOneVerification,
)

random.seed(2302342651)

OUT = Path(__file__).with_name("samples_P001v2.md")

task = ComparatorZeroOneVerification()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task.config.set_level(level)
    for i in range(2):
        x = task.generate_example()
        lines.append(f"### Example {i+1}")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(task.render_prompt(x.metadata))
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(x.metadata["answer"])
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print(OUT)
