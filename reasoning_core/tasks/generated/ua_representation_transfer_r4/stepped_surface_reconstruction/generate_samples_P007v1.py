import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_transfer_r4.stepped_surface_reconstruction.stepped_surface_reconstruction import (
    SteppedSurfaceReconstruction,
)

random.seed(1139467751)

task = SteppedSurfaceReconstruction()

out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"## Level {level}")
    out.append("")
    for _ in range(2):
        e = task.generate_example()
        out.append("### Prompt")
        out.append("")
        out.append(e.prompt)
        out.append("")
        out.append("**Answer**: " + e.answer)
        out.append("")

Path(__file__).with_name("samples_P007v1.md").write_text("\n".join(out))
print("wrote samples_P007v1.md")
