import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_transfer_r1.pitch_class_prime_normal_forms.pitch_class_prime_normal_forms import (
    PitchClassPrimeNormalForms,
)

random.seed(682015719)

task = PitchClassPrimeNormalForms()
lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for i in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {i+1}")
        lines.append(f"**Prompt:** {task.render_prompt(entry.metadata)}")
        lines.append(f"**Answer:** {entry.answer}")
    lines.append("")

Path(__file__).with_name("samples_P008v1.md").write_text("\n".join(lines) + "\n")
