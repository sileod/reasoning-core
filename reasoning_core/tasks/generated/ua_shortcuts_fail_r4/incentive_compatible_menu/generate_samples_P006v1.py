"""Generate samples_P006v1.md: two prompt/answer examples at levels 0, 2 and 5."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.incentive_compatible_menu.incentive_compatible_menu import (
    IncentiveCompatibleMenu,
)

SEED = 798610012
OUT = Path(__file__).with_name("samples_P006v1.md")


def main():
    random.seed(SEED)
    task = IncentiveCompatibleMenu()
    parts = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        parts.append(f"## Level {level}")
        for _ in range(2):
            entry = task.generate_example()
            parts.append("**Prompt**")
            parts.append(entry.prompt)
            parts.append("**Answer**")
            parts.append(entry.answer)
            parts.append("")
    OUT.write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    main()
