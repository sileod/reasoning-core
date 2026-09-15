import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.d_separation.d_separation import (
    d_separation,
)

SEED = 2041304383
OUT = Path(__file__).with_name("samples_P011v1.md")


def main():
    task = d_separation()
    random.seed(SEED)
    lines = []
    lines.append("# d_separation samples")
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            entry = task.generate_example()
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
