import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_interacting_updates_r4.periodic_weave_reconstruction.periodic_weave_reconstruction import (
    PeriodicWeaveReconstruction,
)

SEED = 4238614268
OUT = Path(__file__).with_name("samples_P001v3.md")

random.seed(SEED)
task = PeriodicWeaveReconstruction()

lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for _ in range(2):
        x = task.generate_example()
        lines.append(x.prompt)
        lines.append("")
        lines.append(f"Answer: {x.answer}")
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT)
