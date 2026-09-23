import random
from pathlib import Path

from reasoning_core.template import Task

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.partial_identification_bounds.partial_identification_bounds import (
    PartialIdentificationBounds,
)


def main():
    random.seed(1211525277)
    task = PartialIdentificationBounds()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append("**Prompt:**")
            lines.append(prompt)
            lines.append("")
            lines.append(f"**Answer:** {entry.answer}")
            lines.append("")
    out = Path(__file__).with_name("samples_P010v2.md")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
