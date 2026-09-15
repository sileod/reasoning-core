import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.prime_power_valuation.prime_power_valuation import (
    PrimePowerValuation,
)

random.seed(1475571465)

task = PrimePowerValuation()
out_path = Path(__file__).with_name("samples_P002v1.md")

lines = []
for level in (0, 2, 5):
    lines.append(f"# Level {level}")
    lines.append("")
    task.config.set_level(level)
    for _ in range(2):
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        lines.append(prompt)
        lines.append("")
        lines.append(f"Answer: {x.answer}")
        lines.append("")

out_path.write_text("\n".join(lines).rstrip("\n") + "\n")
