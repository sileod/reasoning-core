import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.symmetric_polynomial_to_elementary.symmetric_polynomial_to_elementary import (
    SymmetricPolyToElementary,
)

random.seed(1662004003)


def main():
    task = SymmetricPolyToElementary()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append("## Level %d" % level)
        for i in range(2):
            ex = task.generate_example()
            out.append("### Example %d" % (i + 1))
            out.append("**Prompt:**")
            out.append("```")
            out.append(task.render_prompt(ex.metadata))
            out.append("```")
            out.append("**Answer:**")
            out.append("```")
            out.append(ex.answer)
            out.append("```")
            out.append("")
    path = Path(__file__).with_name("samples_P001v1.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
