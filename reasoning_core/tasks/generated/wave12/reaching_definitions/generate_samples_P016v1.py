import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.reaching_definitions.reaching_definitions import (
    ReachingDefinitions,
)

OUT = Path(__file__).with_name("samples_P016v1.md")

LEVELS = [0, 2, 5]


def main():
    random.seed(2640394)
    lines = []
    for lvl in LEVELS:
        lines.append(f"# Level {lvl}")
        task = ReachingDefinitions()
        for _ in range(2):
            e = task.generate_example(level=lvl)
            prompt = task.render_prompt(e.metadata)
            lines.append("## Example")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
