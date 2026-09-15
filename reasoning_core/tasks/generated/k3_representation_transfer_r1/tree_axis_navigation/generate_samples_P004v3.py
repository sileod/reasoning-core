import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_transfer_r1.tree_axis_navigation.tree_axis_navigation import (
    TreeAxisConfig,
    TreeAxisNavigation,
)

OUT = Path(__file__).with_name("samples_P004v3.md")

random.seed(1339177894)


def _render(task, level, count):
    task.config.set_level(level)
    lines = []
    for _ in range(count):
        ex = task.generate_example()
        lines.append(f"## Example\n\n{ex.prompt}\n\nAnswer: {ex.answer}\n")
    return "\n".join(lines)


def main():
    task = TreeAxisNavigation(config=TreeAxisConfig())
    parts = []
    for level in (0, 2, 5):
        parts.append(f"# Level {level}\n\n{_render(task, level, 2)}")
    OUT.write_text("\n\n".join(parts))


if __name__ == "__main__":
    main()
