import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_psychometrics_r4.partitioned_block_surface_signatures.partitioned_block_surface_signatures import (
    PartitionedBlockSurfaceSignatures,
)

random.seed(3536382515)

task = PartitionedBlockSurfaceSignatures()
out = []
for level in (0, 2, 5):
    out.append(f"## Level {level}\n")
    for _ in range(2):
        entry = task.generate_example(level=level)
        out.append("### Example\n")
        out.append("**Prompt:**\n\n")
        out.append(task.render_prompt(entry.metadata) + "\n\n")
        out.append("**Answer:**\n\n")
        out.append(entry.answer + "\n\n")

Path(__file__).with_name("samples_P004v1.md").write_text("".join(out))
