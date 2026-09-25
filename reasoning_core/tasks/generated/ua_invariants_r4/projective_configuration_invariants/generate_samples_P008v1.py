import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_invariants_r4.projective_configuration_invariants.projective_configuration_invariants import (
    ProjectiveConfigurationInvariants,
)

random.seed(682015719)

task = ProjectiveConfigurationInvariants()

out = ["# P008v1 samples\n"]

for level in (0, 2, 5):
    out.append(f"\n## Level {level}\n")
    task.config.set_level(level)
    for i in range(2):
        x = task.generate_example()
        out.append(f"### Example {i + 1}\n")
        out.append(f"**Prompt:**\n{task.render_prompt(x.metadata)}\n")
        out.append(f"**Answer:** {x.answer}\n")

Path(__file__).with_name("samples_P008v1.md").write_text("\n".join(out), encoding="utf-8")
print("wrote samples_P008v1.md")
