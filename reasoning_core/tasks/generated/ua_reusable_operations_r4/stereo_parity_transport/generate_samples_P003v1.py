"""Byte-reproducible sample generator for stereochemical_parity_transport."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_reusable_operations_r4.stereochemical_parity_transport.stereochemical_parity_transport import (
    StereoParityTransport,
)

SEED = 2267388306
OUT = Path(__file__).with_name("samples_P003v1.md")

LEVELS = (0, 2, 5)
PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = StereoParityTransport()
    lines = []
    lines.append("# Stereochemical parity transport (P003v1)")
    lines.append("")
    for level in LEVELS:
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(PER_LEVEL):
            ex = task.generate_example(level=level)
            lines.append("### Prompt")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
