import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.shifted_consensus_reconstruction.shifted_consensus_reconstruction import (
    ShiftedConsensusReconstruction,
)

random.seed(729651269)

task = ShiftedConsensusReconstruction()

lines = []
for level in (0, 2, 5):
    lines.append(f"# Level {level}\n")
    task.config.set_level(level)
    for i in range(2):
        ex = task.generate_example()
        lines.append(task.render_prompt(ex.metadata))
        lines.append(f"\nAnswer: {ex.answer}\n")

out = Path(__file__).with_name("samples_P005v1.md")
out.write_text("\n".join(lines))
print(out)
