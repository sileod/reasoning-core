import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_algorithms_and_data_structures_r4.sowing_game_simulation.sowing_game_simulation import (
    SowingGameSimulation,
)

random.seed(4238614268)

task = SowingGameSimulation()
out = []
for level in (0, 2, 5):
    out.append(f"## Level {level}")
    out.append("")
    for _ in range(2):
        ex = task.generate_example(level=level)
        out.append("Prompt:")
        out.append("")
        out.append(ex.prompt)
        out.append("")
        out.append("Answer:")
        out.append("")
        out.append(ex.answer)
        out.append("")

Path(__file__).with_name("samples_P001v3.md").write_text("\n".join(out) + "\n")
