import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_non_local_structured_r4.heap_splitting_nimber_recursion.heap_split_nimber import (
    HeapSplitNimber,
)

random.seed(3536382515)

OUT = Path(__file__).with_name("samples_P004v1.md")


def main():
    task = HeapSplitNimber()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"# Level {level}")
        lines.append("")
        for i in range(2):
            entry = task.generate_example()
            lines.append(f"**Example {i + 1}**")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append(f"**Answer:** {entry.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
