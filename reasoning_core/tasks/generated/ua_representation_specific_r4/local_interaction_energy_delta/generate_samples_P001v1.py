import random
import os

seed = 1662004003
random.seed(seed)

from reasoning_core.tasks.generated.ua_representation_specific_r4.local_interaction_energy_delta.local_interaction_energy_delta import (
    LocalInteractionEnergyDelta, LatticeConfig,
)


def emit(level):
    cfg = LatticeConfig()
    cfg.set_level(level)
    task = LocalInteractionEnergyDelta()
    task.config = cfg
    lines = [f"### Level {level}"]
    for _ in range(2):
        x = task.generate_example()
        lines.append("\n")
        lines.append("Prompt:")
        lines.append(task.render_prompt(x.metadata))
        lines.append("\nAnswer:")
        lines.append(x.answer)
    return "\n".join(lines)


parts = []
for lvl in (0, 2, 5):
    parts.append(emit(lvl))

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "samples_P001v1.md"), "w") as f:
    f.write("\n".join(parts) + "\n")
