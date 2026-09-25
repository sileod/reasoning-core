import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_multi_relation_integration_r5.constraint_based_skeleton_orientation.constraint_based_skeleton_orientation import (
    ConstraintBasedSkeletonOrientation,
)


def main():
    random.seed(1662004003)
    task = ConstraintBasedSkeletonOrientation()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for _ in range(2):
            x = task.generate_example()
            out.append("### Prompt\n")
            out.append(task.render_prompt(x.metadata) + "\n")
            out.append("### Answer\n")
            out.append(x.answer + "\n")
        out.append("\n")
    Path(__file__).with_name("samples_P001v1.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
