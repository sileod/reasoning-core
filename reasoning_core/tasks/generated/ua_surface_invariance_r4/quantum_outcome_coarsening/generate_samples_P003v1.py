import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_surface_invariance_r4.quantum_outcome_coarsening.quantum_outcome_coarsening import (
    QuantumOutcomeCoarsening,
    QuantumOutcomeCoarseningV1Config,
)

random.seed(2267388306)
OUT = Path(__file__).with_name("samples_P003v1.md")


def render(level, n):
    task = QuantumOutcomeCoarsening()
    task.config = QuantumOutcomeCoarseningV1Config()
    task.config.set_level(level)
    blocks = []
    for _ in range(n):
        ex = task.generate_example()
        blocks.append(f"**Prompt:**\n\n{ex.prompt}\n\n**Answer:**\n\n{ex.answer}\n")
    return "\n".join(blocks)


levels = {0: 2, 2: 2, 5: 2}
lines = []
for lv in sorted(levels):
    lines.append(f"## Level {lv}\n")
    lines.append(render(lv, levels[lv]))
    lines.append("\n")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
