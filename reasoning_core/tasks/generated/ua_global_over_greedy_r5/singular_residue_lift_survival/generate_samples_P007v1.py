import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_global_over_greedy_r5.singular_residue_lift_survival.task_singular_residue_lift_survival import (
    SingularResidueLiftSurvival,
)

random.seed(1139467751)

task = SingularResidueLiftSurvival()

out_lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out_lines.append(f"# Level {level}")
    for _ in range(2):
        entry = task.generate_example()
        out_lines.append("Prompt:")
        out_lines.append(entry.prompt)
        out_lines.append("Answer:")
        out_lines.append(entry.answer)
        out_lines.append("")
    out_lines.append("")

Path(__file__).with_name("samples_P007v1.md").write_text("\n".join(out_lines))
