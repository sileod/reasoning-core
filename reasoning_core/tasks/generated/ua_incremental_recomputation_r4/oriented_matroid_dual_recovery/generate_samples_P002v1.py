import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.oriented_matroid_dual_recovery.oriented_matroid_dual_recovery import (
    OrientedMatroidDualRecovery,
)

random.seed(1475571465)

task = OrientedMatroidDualRecovery()
out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"# Level {level}")
    for _ in range(2):
        e = task.generate_example()
        out.append("## Example")
        out.append(task.render_prompt(e.metadata))
        out.append("Answer:")
        out.append(e.answer)
        out.append("")
    out.append("")

Path(__file__).with_name("samples_P002v1.md").write_text("\n".join(out) + "\n")
