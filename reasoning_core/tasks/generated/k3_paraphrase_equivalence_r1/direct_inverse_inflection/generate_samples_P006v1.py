"""Generate samples_P006v1.md for the direct-inverse inflection trial."""

import random
from pathlib import Path

random.seed(798610012)

from direct_inverse_inflection import DirectInverseInflection

OUT = Path(__file__).with_name("samples_P006v1.md")
LEVELS = ((0, 2), (2, 2), (5, 2))


def build():
    task = DirectInverseInflection()
    sections = ["# Samples — P006v1 direct_inverse_inflection", ""]
    for level, count in LEVELS:
        task.config.set_level(level)
        sections.append(f"## Level {level}")
        sections.append("")
        for _ in range(count):
            e = task.generate_example()
            sections.append("### Prompt")
            sections.append("")
            sections.append(e.metadata["_prompt_text"] if "_prompt_text" in e.metadata
                            else task.render_prompt(e.metadata))
            sections.append("")
            sections.append("### Answer")
            sections.append("")
            sections.append(e.answer)
            sections.append("")
    OUT.write_text("\n".join(sections), encoding="utf-8")


if __name__ == "__main__":
    build()
