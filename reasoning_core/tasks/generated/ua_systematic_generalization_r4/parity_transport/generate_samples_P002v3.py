"""Byte-reproducible sample generation for trial P002v3."""
import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.stereochemical_parity_transport.parity_transport_v3 import (
    ParityTransportV3,
)

SEED = 368817805
OUT = Path(__file__).with_name("samples_P002v3.md")

random.seed(SEED)


def _samples_for_level(level, n):
    task = ParityTransportV3()
    task.config.set_level(level)
    return [task.generate_example() for _ in range(n)]


def main():
    lines = []
    for level, n in ((0, 2), (2, 2), (5, 2)):
        lines.append(f"# Level {level}")
        lines.append("")
        for i, ex in enumerate(_samples_for_level(level, n), 1):
            prompt = ex.prompt
            lines.append(f"## Example {i}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
