import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r4.implicative_factive_inference.implicative_factive_inference import (
    ImplicativeFactiveInference,
)

random.seed(1662004003)


def render(task, x):
    return task.render_prompt(x.metadata)


def main():
    task = ImplicativeFactiveInference()
    out = Path(__file__).with_name("samples_P001v1.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"# Level {level}")
        for i in range(2):
            x = task.generate_example()
            lines.append(f"## Example {i+1}")
            lines.append(f"Prompt: {render(task, x)}")
            lines.append(f"Answer: {x.answer}")
            lines.append("")
    out.write_text("\n".join(lines))
    print(out.read_text())


if __name__ == "__main__":
    main()
