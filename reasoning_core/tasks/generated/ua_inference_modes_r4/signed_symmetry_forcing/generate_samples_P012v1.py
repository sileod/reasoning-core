"""Reproducible sample generator for trial P012v1 (signed_symmetry_forcing).

Seeded globally so the whole file is byte-reproducible across processes.
Writes samples_P012v1.md next to itself with two prompt/answer examples at
levels 0, 2 and 5.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.signed_symmetry_forcing.signed_symmetry_forcing import (
    SignedSymmetryForcing,
)

SEED = 1277236794
OUT = Path(__file__).with_name("samples_P012v1.md")


def main():
    random.seed(SEED)
    task = SignedSymmetryForcing()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("## Level %d" % level)
        for _ in range(2):
            entry = task.generate_example()
            lines.append("")
            lines.append("Prompt:\n\n%s" % entry.prompt)
            lines.append("")
            lines.append("Answer: %s" % entry.answer)
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
