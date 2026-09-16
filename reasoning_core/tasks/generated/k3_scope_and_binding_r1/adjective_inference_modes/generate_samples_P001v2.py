import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.adjective_inference_modes.adjective_inference_modes import (
    AdjectiveInferenceModes,
)

random.seed(2302342651)

task = AdjectiveInferenceModes()

out = Path(__file__).with_name("samples_P001v2.md")
lines = [
    "# Samples for adjective_inference_modes (P001v2)",
    "",
]

for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for k in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {k + 1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(entry.metadata["prompt"])
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(entry.answer)
        lines.append("")

out.write_text("\n".join(lines))
