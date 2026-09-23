import random
from pathlib import Path

random.seed(1139467751)

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.turnpike_distance_reconstruction.turnpike_distance_reconstruction import (
    TurnpikeDistanceReconstruction,
)

OUT = Path(__file__).with_name("samples_P007v1.md")


def main():
    task = TurnpikeDistanceReconstruction()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example(level=level)
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
