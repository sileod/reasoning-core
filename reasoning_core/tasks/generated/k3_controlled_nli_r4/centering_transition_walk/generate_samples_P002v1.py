import random
from pathlib import Path

random.seed(1475571465)

from reasoning_core.tasks.generated.k3_controlled_nli_r4.centering_transition_walk.module import (
    CenteringTransitionWalk,
)

out = Path(__file__).with_name("samples_P002v1.md")
lines = []
for level in (0, 2, 5):
    task = CenteringTransitionWalk()
    task.config.set_level(level)
    lines.append(f"Level {level}")
    for i in range(2):
        x = task.generate_example()
        lines.append("Prompt:")
        lines.append(task.render_prompt(x.metadata))
        lines.append("Answer:")
        lines.append(x.answer)
        lines.append("")
lines.append("")
out.write_text("\n".join(lines) + "\n")
print(f"wrote {out}")
