import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_uncertainty_r1.censored_survival_estimate.censored_survival_estimate import CensoredSurvivalEstimate

random.seed(1139467751)

out = Path(__file__).with_name("samples_P007v1.md")
task = CensoredSurvivalEstimate()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task.config.set_level(level)
    lines.append("")
    for k in range(2):
        x = task.generate_example()
        lines.append(f"### Example {k + 1}")
        lines.append("")
        lines.append("Prompt:")
        lines.append("```")
        lines.append(task.render_prompt(x.metadata))
        lines.append("```")
        lines.append("")
        lines.append("Answer:")
        lines.append("```")
        lines.append(x.answer)
        lines.append("```")
        lines.append("")

out.write_text("\n".join(lines))
print(f"wrote {out}")
