import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_global_from_local_r4.nonogram_fixpoint_propagation.nonogram_fixpoint_propagation import NonogramFixpointPropagation


def main():
    random.seed(2409743872)
    task = NonogramFixpointPropagation()
    out = Path(__file__).with_name("samples_P010v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"## Example {i + 1}")
            lines.append(f"**Prompt:**")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append(f"**Answer:** {ex.answer}")
            lines.append("")
    out.write_text("\n".join(lines))
    print(out)


if __name__ == "__main__":
    main()
