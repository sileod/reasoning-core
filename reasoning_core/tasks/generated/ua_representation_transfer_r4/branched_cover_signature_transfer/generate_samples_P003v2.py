import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_transfer_r4.branched_cover_signature_transfer.branched_cover_signature_transfer import (
    BranchedCoverSignatureTransfer,
)

random.seed(382564971)

task = BranchedCoverSignatureTransfer()
lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for i in range(2):
        entry = task.generate_example()
        lines.append(f"### Example {i+1}")
        lines.append(f"**Prompt:** {task.render_prompt(entry.metadata)}")
        lines.append(f"**Answer:** {entry.answer}")
    lines.append("")

Path(__file__).with_name("samples_P003v2.md").write_text("\n".join(lines) + "\n")
