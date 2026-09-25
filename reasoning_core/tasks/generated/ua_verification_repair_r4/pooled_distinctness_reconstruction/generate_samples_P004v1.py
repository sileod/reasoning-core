import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_verification_repair_r4.pooled_distinctness_reconstruction.pooled_distinctness_reconstruction import (
    PooledDistinctnessReconstruction,
)

random.seed(3536382515)

OUT = Path(__file__).with_name("samples_P004v1.md")

t = PooledDistinctnessReconstruction()

blocks = ["# Samples P004v1", ""]
for level in (0, 2, 5):
    t.config.set_level(level)
    blocks.append(f"## Level {level}")
    blocks.append("")
    for idx in range(2):
        e = t.generate_example()
        blocks.append(f"### Example {idx + 1}")
        blocks.append("")
        blocks.append("**Prompt:**")
        blocks.append("")
        blocks.append(e.prompt)
        blocks.append("")
        blocks.append("Answer:")
        blocks.append("")
        blocks.append(e.answer)
        blocks.append("")

OUT.write_text("\n".join(blocks) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
