import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_verification_repair_r1.lindenmayer_parallel_rewrite.lindenmayer_parallel_rewrite import (
    LindenmayerParallelRewrite,
)

random.seed(214538085)

OUT = Path(__file__).with_name("samples_P012v2.md")


def render(task, entry):
    return task.render_prompt(entry.metadata) + "\n\nAnswer: " + entry.answer


def main():
    task = LindenmayerParallelRewrite()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(2):
            entry = task.generate_example()
            lines.append(f"## Example {i + 1}")
            lines.append("")
            prompt = task.render_prompt(entry.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
