"""Generate samples_P006v1.md for the inverse-variance pooling task."""
import pathlib
import random

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.inverse_variance_pooling.inverse_variance_pooling import (
    InverseVariancePooling,
)

random.seed(798610012)

OUT = pathlib.Path(__file__).with_name("samples_P006v1.md")


def render(task, level):
    task.config.set_level(level)
    ex = task.generate_example()
    return task.render_prompt(ex.metadata), ex.answer


def main():
    task = InverseVariancePooling()
    task.generate_example()  # warm build
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        for j in range(2):
            prompt, answer = render(task, level)
            lines.append(f"## Example {j + 1}")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
