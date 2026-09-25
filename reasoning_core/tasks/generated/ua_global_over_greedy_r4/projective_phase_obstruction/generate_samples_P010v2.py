import random
from pathlib import Path

random.seed(1211525277)

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.projective_phase_obstruction.projective_phase_obstruction import (
    ProjectivePhaseObstruction,
)

OUT = Path(__file__).with_name("samples_P010v2.md")

LEVELS = {0: 2, 2: 2, 5: 2}

lines = []
lines.append("# Samples")

for level in (0, 2, 5):
    lines.append("")
    lines.append("## Level %d" % level)
    for _ in range(LEVELS[level]):
        t = ProjectivePhaseObstruction()
        t.config.set_level(level)
        x = t.generate_example()
        lines.append("")
        lines.append("### prompt")
        lines.append(x.prompt)
        lines.append("")
        lines.append("### Answer")
        lines.append(x.answer)

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT)
