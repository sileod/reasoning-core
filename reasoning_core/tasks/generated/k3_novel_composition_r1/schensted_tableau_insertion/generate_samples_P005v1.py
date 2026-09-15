import random
from pathlib import Path

random.seed(729651269)

from reasoning_core.tasks.generated.k3_novel_composition_r1.schensted_tableau_insertion.schensted_tableau_insertion import (
    SchenstedTableauInsertion,
)

OUT = Path(__file__).with_name("samples_P005v1.md")


def emit(level):
    task = SchenstedTableauInsertion()
    task.config.set_level(level)
    lines = [f"## Level {level}"]
    for _ in range(2):
        e = task.generate_example()
        lines.append("### Prompt")
        lines.append(task.render_prompt(e.metadata))
        lines.append("### Answer")
        lines.append(e.answer)
    return lines


def main():
    parts = ["# Samples P005v1", ""]
    for level in (0, 2, 5):
        parts.extend(emit(level))
        parts.append("")
    OUT.write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    main()
