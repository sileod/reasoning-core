import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_state_tracking_r4.switched_capacitor_charge_tracking.switched_capacitor_charge_tracking import (
    SwitchedCapacitorChargeTracking,
)

SEED = 2409743872
N_PER_LEVEL = 3
LEVELS = [0, 2, 5]

random.seed(SEED)

out = Path(__file__).with_name("samples_P010v1.md")
task = SwitchedCapacitorChargeTracking()

lines = []
lines.append("# P010v1 samples - switched_capacitor_charge_tracking")
lines.append("")
lines.append(f"Seed: {SEED}")
lines.append("")
for level in LEVELS:
    lines.append(f"## Level {level}")
    lines.append("")
    task.config.set_level(level)
    for i in range(N_PER_LEVEL):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append(f"### Example {i + 1}")
        lines.append("")
        lines.append("Prompt:")
        lines.append("")
        lines.append("```")
        lines.append(prompt)
        lines.append("```")
        lines.append("")
        lines.append(f"Answer: {ex.answer}")
        lines.append("")

out.write_text("\n".join(lines) + "\n")
print(f"Wrote {out}")
