"""Generate samples_P012v1.md for the Ershov register numbering task."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.ershov_register_numbering.ershov_register_numbering import (
    ErshovRegisterNumbering,
)

SEED = 1277236794
OUT = Path(__file__).with_name("samples_P012v1.md")


def main():
    random.seed(SEED)
    task = ErshovRegisterNumbering()
    lines = []
    lines.append("# Samples P012v1: Ershov register numbering")
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            e = task.generate_example()
            prompt = task.render_prompt(e.metadata)
            answer = e.answer
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
