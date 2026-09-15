import random
from pathlib import Path

from reasoning_core.template import Task
from reasoning_core.tasks.generated.k3_systematic_generalization_r1.birkhoff_decomposition.birkhoff import (
    BirkhoffDecomposition,
)


random.seed(798610012)


def _render_example(level):
    task = BirkhoffDecomposition()
    task.config.set_level(level)
    ex = task.generate_example()
    return ex.answer, task.render_prompt(ex.metadata)


def main():
    out = Path(__file__).with_name("samples_P006v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        for i in range(2):
            answer, prompt = _render_example(level)
            lines.append(f"## Example {i + 1}")
            lines.append("Prompt:")
            lines.append(prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append(answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
