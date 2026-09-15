"""Generate samples_P002v1.md for the exact_cover_selection task."""

import random
from pathlib import Path

from exact_cover_selection import ExactCoverSelection

SEED = 1475571465
OUT = Path(__file__).with_name("samples_P002v1.md")


def main():
    random.seed(SEED)
    task = ExactCoverSelection()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            e = task.generate_example()
            prompt = task.render_prompt(e.metadata)
            lines.append("### Example")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(f"`{e.answer}`")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
