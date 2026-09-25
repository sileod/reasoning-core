import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_reusable_operations_r4.merkle_inclusion_path_checking.merkle_inclusion_path_checking import (
    MerkleInclusionPathChecking,
)

random.seed(798610012)

OUT = Path(__file__).with_name("samples_P006v1.md")
TASK = MerkleInclusionPathChecking()

lines = ["# Merkle inclusion path checking - variant 1 (P006v1)", ""]
for level in (0, 2, 5):
    TASK.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for _ in range(2):
        ex = TASK.generate_example()
        lines.append("### Example")
        lines.append("")
        lines.append(ex.prompt)
        lines.append("")
        lines.append(f"**Answer:** {ex.answer}")
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print(f"wrote {OUT}")
