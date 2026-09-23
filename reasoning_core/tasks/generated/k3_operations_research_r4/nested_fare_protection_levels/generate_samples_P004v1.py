import pathlib
import random

from reasoning_core.tasks.generated.k3_operations_research_r4.nested_fare_protection_levels.nested_fare_protection_levels import (  # noqa
    NestedFareProtectionLevels,
)

SEED = 3536382515
OUT = pathlib.Path(__file__).with_name("samples_P004v1.md")
LEVELS = (0, 2, 5)


def main():
    random.seed(SEED)
    task = NestedFareProtectionLevels()
    lines = []
    for level in LEVELS:
        lines.append(f"# Level {level}\n")
        for _ in range(2):
            entry = task.generate_example(level=level)
            lines.append(entry.prompt + "\n")
            lines.append(f"Answer: {entry.answer}\n")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
