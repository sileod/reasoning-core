import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relational_structures_r1.kinship_relation_resolution.kinship_relation_resolution import (
    KinshipRelationResolution,
)

SEED = 1662004003


def main():
    random.seed(SEED)
    task = KinshipRelationResolution()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"# Level {level}\n")
        for i in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            out.append(f"## Example {i + 1}\n")
            out.append("Prompt:\n")
            out.append(prompt)
            out.append("\n")
            out.append(f"Answer: {ex.answer}\n")
        out.append("\n")
    path = Path(__file__).with_name("samples_P001v1.md")
    path.write_text("".join(out), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
