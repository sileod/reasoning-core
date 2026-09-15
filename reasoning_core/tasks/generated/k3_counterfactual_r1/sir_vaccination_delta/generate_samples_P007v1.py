import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_counterfactual_r1.sir_vaccination_delta.sir_vaccination_delta import (
    SirVaccinationDelta,
)

random.seed(1139467751)

task = SirVaccinationDelta()
out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append("## Level %d" % level)
    for _ in range(2):
        ex = task.generate_example()
        out.append("### Prompt")
        out.append(task.render_prompt(ex.metadata))
        out.append("")
        out.append("### Answer")
        out.append(ex.answer)
        out.append("")
    out.append("")

out_path = Path(__file__).with_name("samples_P007v1.md")
out_path.write_text("\n".join(out))
print(out_path.resolve())
