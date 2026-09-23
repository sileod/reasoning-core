"""Generate samples_P004v1.md: two prompt/answer examples at levels 0, 2 and 5.

Byte-reproducible: seeded once with seed 3536382515; module-level random functions
only. Output is written next to this script.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_inference_modes_r4.xor_peeling_recovery.xor_peeling_recovery import (
    XORPeelingRecovery,
)

SEED = 3536382515
LEVELS = (0, 2, 5)
PER_LEVEL = 2

random.seed(SEED)

task = XORPeelingRecovery()

out = []
out.append("# XOR Peeling Recovery Samples (P004v1)")
out.append("")

for level in LEVELS:
    task.config.set_level(level)
    out.append("## Level %d" % level)
    out.append("")
    for i in range(PER_LEVEL):
        ex = task.generate_example()
        out.append("### Level %d example %d" % (level, i + 1))
        out.append("")
        out.append("**Prompt:**")
        out.append("")
        out.append(ex.prompt)
        out.append("")
        out.append("**Answer:**")
        out.append("")
        out.append(ex.answer)
        out.append("")

path = Path(__file__).with_name("samples_P004v1.md")
path.write_text("\n".join(out), encoding="utf-8")
print("wrote", path)
