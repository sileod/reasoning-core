import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_language_implementation_r4.aries_crash_recovery.aries_crash_recovery import (
    AriesCrashRecovery,
)

random.seed(682015719)

OUT = Path(__file__).with_name("samples_P008v1.md")
LEVELS = (0, 2, 5)
PER_LEVEL = 2

task = AriesCrashRecovery()


def build():
    blocks = ["# Samples P008v1: ARIES crash recovery", ""]
    for level in LEVELS:
        task.config.set_level(level)
        blocks.append(f"## Level {level}")
        blocks.append("")
        for i in range(1, PER_LEVEL + 1):
            entry = task.generate_example()
            blocks.append(f"### Example {i}")
            blocks.append("")
            blocks.append("PROMPT:")
            blocks.append(entry.prompt)
            blocks.append("")
            blocks.append(f"Answer: {entry.answer}")
            blocks.append("")
    OUT.write_text("\n".join(blocks))


if __name__ == "__main__":
    build()
