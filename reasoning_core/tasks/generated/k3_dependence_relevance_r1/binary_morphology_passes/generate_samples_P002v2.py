import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dependence_relevance_r1.binary_morphology_passes.binary_morphology_passes import (
    BinaryMorphologyPasses,
)

random.seed(1336314872)

OUT = Path(__file__).with_name("samples_P002v2.md")


def emit(task, level, lines):
    task.config.set_level(level)
    entry = task.generate_example()
    prompt = task.render_prompt(entry.metadata)
    lines.append(f"## Level {level}")
    lines.append("")
    lines.append(prompt)
    lines.append("")
    lines.append(f"**Answer**: {entry.answer}")
    lines.append("")


def main():
    task = BinaryMorphologyPasses()
    lines = []
    for level in (0, 0, 2, 2, 5, 5):
        emit(task, level, lines)
    OUT.write_text("\n".join(lines) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
