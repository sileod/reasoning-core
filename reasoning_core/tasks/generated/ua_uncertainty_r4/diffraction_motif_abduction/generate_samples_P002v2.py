"""Reproducible sample generator for diffraction_motif_abduction (P002v2)."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.diffraction_motif_abduction.diffraction_motif_abduction import (
    DiffractionMotifAbduction,
)

SEED = 1336314872
LEVELS = (0, 2, 5)
PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = DiffractionMotifAbduction()
    out = Path(__file__).with_name("samples_P002v2.md")
    lines = ["# Diffraction Motif Abduction v2 (P002v2) Samples", ""]
    for level in LEVELS:
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(PER_LEVEL):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0
            lines.append("**Prompt**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
