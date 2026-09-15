import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_uncertainty_r1.announcement_round_deduction.announcement_round_deduction import (
    AnnouncementRoundDeduction,
)

random.seed(1259343118)

out = Path(__file__).with_name("samples_P003v3.md")

lines = []
for level in (0, 2, 5):
    task = AnnouncementRoundDeduction()
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for _ in range(2):
        ex = task.generate_example()
        lines.append("### Example")
        lines.append(ex.prompt)
        lines.append("")
        lines.append(f"Answer: {ex.answer}")
        lines.append("")

out.write_text("\n".join(lines))
print(f"wrote {out}")
