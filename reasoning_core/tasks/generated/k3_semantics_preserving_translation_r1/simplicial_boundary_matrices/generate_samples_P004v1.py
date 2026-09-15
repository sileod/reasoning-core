import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_semantics_preserving_translation_r1.simplicial_boundary_matrices.simplicial_boundary_matrices import (
    SimplicialBoundaryMatrices,
)

SEED = 3536382515

LEVELS = [0, 2, 5]
PER_LEVEL = 2


def main():
    random.seed(SEED)
    out = []
    for level in LEVELS:
        out.append(f"# Level {level}\n")
        task = SimplicialBoundaryMatrices()
        task.config.set_level(level)
        for i in range(PER_LEVEL):
            ex = task.generate_example()
            out.append(f"## Example {i + 1}\n")
            out.append("**Prompt:**\n")
            out.append(task.render_prompt(ex.metadata) + "\n")
            out.append("**Answer:**\n")
            out.append(ex.answer + "\n")
    path = Path(__file__).with_name("samples_P004v1.md")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
