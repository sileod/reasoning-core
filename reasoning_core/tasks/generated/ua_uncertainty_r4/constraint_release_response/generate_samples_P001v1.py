import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.constraint_release_response.constraint_release_response import (
    ConstraintReleaseResponse,
)

random.seed(1662004003)

task = ConstraintReleaseResponse()

out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"## Level {level}")
    for i in range(2):
        ex = task.generate_example()
        out.append(f"### Example {i + 1}")
        out.append("**Prompt:**")
        out.append(ex.prompt)
        out.append("")
        out.append("**Answer:**")
        out.append(ex.answer)
        out.append("")

target = Path(__file__).with_name("samples_P001v1.md")
target.write_text("\n".join(out), encoding="utf-8")
print("wrote", target)
