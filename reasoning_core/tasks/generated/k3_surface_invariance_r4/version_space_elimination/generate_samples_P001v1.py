"""Deterministic sample generation for version_space_elimination."""
import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_surface_invariance_r4.version_space_elimination.version_space_elimination import (
    VersionSpaceElimination)

random.seed(1662004003)
OUT = Path(__file__).with_name("samples_P001v1.md")
task = VersionSpaceElimination()

levels = {0: 2, 2: 2, 5: 2}
parts = ["# Samples: version_space_elimination (P001v1)", ""]
for level in (0, 2, 5):
    parts.append(f"## Level {level}")
    for idx in range(levels[level]):
        entry = task.generate_example(level=level)
        parts.append(f"### Example {idx + 1}")
        parts.append("**Prompt**")
        parts.append(entry.metadata.get("_prompt", task.render_prompt(entry.metadata)))
        parts.append("")
        parts.append("**Answer**")
        parts.append(entry.answer)
        parts.append("")
        parts.append("---")
        parts.append("")

OUT.write_text("\n".join(parts))
print(OUT)
