import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.reduced_matrix_tour_branching.reduced_matrix_tour_branching import (
    ReducedMatrixTourBranching,
)

random.seed(1475571465)

OUT = Path(__file__).with_name("samples_P002v1.md")


def render_matrix(matrix):
    return "\n".join(" ".join(str(v) for v in row) for row in matrix)


lines = []
for level in (0, 2, 5):
    task = ReducedMatrixTourBranching()
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for k in range(2):
        ex = task.generate_example()
        lines.append(f"### Example {k + 1}")
        lines.append("")
        lines.append(ex.prompt)
        lines.append("")
        lines.append("Answer:")
        lines.append("")
        lines.append(ex.answer)
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print(OUT)
