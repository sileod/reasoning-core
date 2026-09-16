import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.tree_pattern_occurrence_count.tree_pattern_occurrence_count import (
    TreePatternOccurrenceCount,
)

random.seed(682015719)

OUT = Path(__file__).with_name("samples_P008v1.md")


def main():
    task = TreePatternOccurrenceCount()
    lines = ["# Tree pattern occurrence count (P008v1)\n"]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}\n")
        for _ in range(2):
            ex = task.generate_example(level=level)
            lines.append("### Example\n")
            lines.append(f"Prompt:\n{ex.prompt}\n")
            lines.append(f"Answer:\n{ex.answer}\n")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
